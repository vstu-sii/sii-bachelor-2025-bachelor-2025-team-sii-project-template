from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Optional, List
import uuid
import tempfile
import os
import asyncio
from pydantic import BaseModel, Field
from datetime import datetime

from ml.service.model_service import LLMAsyncService, get_llm_service, ModelResponse, ModelMetrics
from backend.utils.image_utils import validate_image, save_uploaded_file
from backend.middleware.rate_limit import rate_limit
from ml.tracing.langfuse_config import tracer

router = APIRouter(prefix="/api/v2/ai", tags=["AI Service"])

class AnalysisRequest(BaseModel):
    """Модель запроса для анализа"""
    prompt_variant: str = Field("v1", description="Версия промпта: v1, v2, v3")
    use_cache: bool = Field(True, description="Использовать кэш")
    user_id: Optional[str] = Field(None, description="ID пользователя")
    metadata: Optional[dict] = Field(None, description="Дополнительные метаданные")

class AnalysisResponse(BaseModel):
    """Модель ответа анализа"""
    success: bool
    trace_id: str
    request_id: str
    analysis: dict
    metrics: dict
    timing: dict
    metadata: dict

class BatchAnalysisRequest(BaseModel):
    """Модель запроса для пакетного анализа"""
    analyses: List[dict]  # Список пар изображений
    prompt_variant: str = "v1"
    max_concurrent: int = Field(3, ge=1, le=10)
    user_id: Optional[str] = None

class BatchAnalysisResponse(BaseModel):
    """Модель ответа пакетного анализа"""
    request_id: str
    total: int
    successful: int
    failed: int
    analyses: List[dict]
    timing: dict

@router.post("/analyze", response_model=AnalysisResponse)
@rate_limit(max_requests=10, time_window=60)  # 10 запросов в минуту
async def analyze_cleanliness(
    request: Request,
    clean_image: UploadFile = File(...),
    dirty_image: UploadFile = File(...),
    analysis_request: AnalysisRequest = Depends(),
    service: LLMAsyncService = Depends(get_llm_service)
):
    """
    Асинхронный анализ чистоты квартиры
    
    Поддерживает:
    - Multiple prompt variants (A/B тестирование)
    - Кэширование результатов
    - Подробные метрики производительности
    """
    trace_id = str(uuid.uuid4())
    request_id = str(uuid.uuid4())
    start_time = datetime.now()
    
    # Валидация файлов
    if not clean_image.content_type.startswith('image/') or not dirty_image.content_type.startswith('image/'):
        raise HTTPException(400, "Both files must be images")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            # Сохранение файлов
            clean_path, dirty_path = await asyncio.gather(
                save_uploaded_file(clean_image, tmpdir),
                save_uploaded_file(dirty_image, tmpdir)
            )
            
            # Валидация
            await asyncio.gather(
                validate_image(clean_path),
                validate_image(dirty_path)
            )
            
            # Анализ
            response, metrics = await service.analyze_cleanliness(
                clean_image_path=clean_path,
                dirty_image_path=dirty_path,
                prompt_variant=analysis_request.prompt_variant,
                use_cache=analysis_request.use_cache,
                user_id=analysis_request.user_id,
                trace_id=trace_id
            )
            
            end_time = datetime.now()
            
            # Формирование ответа
            result = AnalysisResponse(
                success=response.success,
                trace_id=trace_id,
                request_id=request_id,
                analysis={
                    "defects": response.defects,
                    "score": response.score,
                    "recommendations": response.recommendations,
                    "defects_count": len(response.defects)
                },
                metrics={
                    "inference_time": round(metrics.inference_time, 3),
                    "token_count": metrics.token_count,
                    "prompt_tokens": metrics.prompt_tokens,
                    "completion_tokens": metrics.completion_tokens,
                    "cache_hit": metrics.cache_hit
                },
                timing={
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat(),
                    "total_seconds": (end_time - start_time).total_seconds()
                },
                metadata={
                    **response.metadata,
                    "user_id": analysis_request.user_id,
                    "client_ip": request.client.host if request.client else None,
                    "user_agent": request.headers.get("user-agent", "")
                }
            )
            
            # Логирование
            logger.info(f"Analysis completed: {request_id}, score: {response.score}, time: {metrics.inference_time:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"Analysis failed: {request_id}, error: {e}")
            
            tracer.trace_error(
                trace_id=trace_id,
                name="api_analysis_error",
                error=str(e),
                input_data={
                    "request_id": request_id,
                    "prompt_variant": analysis_request.prompt_variant
                },
                user_id=analysis_request.user_id
            )
            
            raise HTTPException(500, f"Analysis failed: {str(e)}")

@router.post("/analyze-batch", response_model=BatchAnalysisResponse)
@rate_limit(max_requests=2, time_window=60)  # 2 пакетных запроса в минуту
async def analyze_batch(
    request: BatchAnalysisRequest,
    service: LLMAsyncService = Depends(get_llm_service)
):
    """
    Пакетный анализ нескольких пар изображений
    
    Позволяет обрабатывать до 10 пар одновременно с ограничением
    на количество одновременных запросов к модели.
    """
    request_id = str(uuid.uuid4())
    start_time = datetime.now()
    
    if len(request.analyses) > 10:
        raise HTTPException(400, "Maximum 10 analyses per batch")
    
    # Подготовка временных файлов
    analyses_data = []
    temp_dirs = []
    
    try:
        for i, analysis in enumerate(request.analyses):
            tmpdir = tempfile.mkdtemp()
            temp_dirs.append(tmpdir)
            
            # Здесь должна быть логика загрузки изображений из base64 или URL
            # Для примера предполагаем, что изображения передаются как base64
            clean_path = os.path.join(tmpdir, f"clean_{i}.jpg")
            dirty_path = os.path.join(tmpdir, f"dirty_{i}.jpg")
            
            analyses_data.append({
                "id": i,
                "clean_path": clean_path,
                "dirty_path": dirty_path,
                "metadata": analysis.get("metadata", {})
            })
        
        # Создание семафора для ограничения одновременных запросов
        semaphore = asyncio.Semaphore(request.max_concurrent)
        
        async def process_analysis(analysis_data):
            async with semaphore:
                try:
                    response, metrics = await service.analyze_cleanliness(
                        clean_image_path=analysis_data["clean_path"],
                        dirty_image_path=analysis_data["dirty_path"],
                        prompt_variant=request.prompt_variant,
                        user_id=request.user_id
                    )
                    
                    return {
                        "id": analysis_data["id"],
                        "success": True,
                        "score": response.score,
                        "defects_count": len(response.defects),
                        "inference_time": metrics.inference_time,
                        "cache_hit": metrics.cache_hit,
                        "metadata": analysis_data["metadata"]
                    }
                except Exception as e:
                    return {
                        "id": analysis_data["id"],
                        "success": False,
                        "error": str(e),
                        "metadata": analysis_data["metadata"]
                    }
        
        # Параллельная обработка
        tasks = [process_analysis(ad) for ad in analyses_data]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Обработка результатов
        successful = 0
        failed = 0
        processed_results = []
        
        for result in results:
            if isinstance(result, Exception):
                failed += 1
                processed_results.append({"error": str(result)})
            elif result.get("success"):
                successful += 1
                processed_results.append(result)
            else:
                failed += 1
                processed_results.append(result)
        
        end_time = datetime.now()
        
        return BatchAnalysisResponse(
            request_id=request_id,
            total=len(analyses_data),
            successful=successful,
            failed=failed,
            analyses=processed_results,
            timing={
                "start": start_time.isoformat(),
                "end": end_time.isoformat(),
                "total_seconds": (end_time - start_time).total_seconds()
            }
        )
        
    finally:
        # Очистка временных файлов
        for tmpdir in temp_dirs:
            try:
                import shutil
                shutil.rmtree(tmpdir, ignore_errors=True)
            except:
                pass

@router.get("/service/stats")
async def get_service_stats(
    service: LLMAsyncService = Depends(get_llm_service)
):
    """Получение статистики сервиса"""
    stats = await service.get_service_stats()
    return {
        "service": "llm_async_service",
        "status": "running",
        "stats": stats,
        "timestamp": datetime.now().isoformat()
    }

@router.post("/prompt-test")
async def test_prompt_variant(
    prompt_variant: str,
    test_text: str,
    service: LLMAsyncService = Depends(get_llm_service)
):
    """
    Тестирование различных промптов
    
    Позволяет протестировать, как модель отвечает на разные промпты
    без фактического анализа изображений.
    """
    if prompt_variant not in service.prompt_variants:
        raise HTTPException(400, f"Unknown prompt variant. Available: {list(service.prompt_variants.keys())}")
    
    prompt_func = service.prompt_variants[prompt_variant]
    prompt = prompt_func()
    
    # Примерная логика тестирования промпта
    test_data = {
        "prompt_variant": prompt_variant,
        "prompt_length": len(prompt),
        "prompt_preview": prompt[:200] + "..." if len(prompt) > 200 else prompt,
        "test_response": f"Prompt '{prompt_variant}' would process: {test_text[:100]}..."
    }
    
    return test_data

@router.post("/cache/clear")
async def clear_cache(
    pattern: str = "llava:*",
    service: LLMAsyncService = Depends(get_llm_service)
):
    """Очистка кэша"""
    if not service.redis_client:
        return {"message": "Cache not enabled"}
    
    try:
        keys = await service.redis_client.keys(pattern)
        if keys:
            await service.redis_client.delete(*keys)
            return {
                "message": f"Cache cleared",
                "keys_deleted": len(keys)
            }
        else:
            return {"message": "No keys found"}
    except Exception as e:
        raise HTTPException(500, f"Cache clear failed: {e}")