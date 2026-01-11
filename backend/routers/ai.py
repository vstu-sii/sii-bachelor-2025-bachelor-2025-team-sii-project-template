from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import Optional
import uuid
import tempfile
import os
from pydantic import BaseModel
from ml.models.baseline import LLavaBaselineModel
from ml.tracing.langfuse_config import tracer
from backend.utils.image_utils import validate_image, save_uploaded_file

router = APIRouter(prefix="/api/v1/ai", tags=["AI Analysis"])
model = LLavaBaselineModel()

class CleanlinessAnalysisRequest(BaseModel):
    """Модель запроса для анализа чистоты"""
    user_id: Optional[str] = None
    metadata: Optional[dict] = None

class CleanlinessAnalysisResponse(BaseModel):
    """Модель ответа анализа чистоты"""
    success: bool
    trace_id: str
    result: dict
    metrics: dict
    model_info: dict

@router.post("/analyze-cleanliness", response_model=CleanlinessAnalysisResponse)
async def analyze_cleanliness(
    clean_image: UploadFile = File(...),
    dirty_image: UploadFile = File(...),
    request: CleanlinessAnalysisRequest = Depends(),
    trace_id: Optional[str] = None
):
    """
    Анализирует чистоту квартиры по двум изображениям
    
    - **clean_image**: Эталонное (чистое) изображение квартиры
    - **dirty_image**: Оцениваемое изображение квартиры
    - **user_id**: Опциональный ID пользователя для трассировки
    - **trace_id**: Опциональный ID трассировки (если не указан, генерируется)
    - **metadata**: Дополнительные метаданные
    
    Возвращает анализ с недостатками, оценкой и рекомендациями.
    """
    # Генерируем trace_id если не предоставлен
    if not trace_id:
        trace_id = str(uuid.uuid4())
    
    # Создаем временные файлы
    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            # Сохраняем загруженные файлы
            clean_path = await save_uploaded_file(clean_image, tmpdir)
            dirty_path = await save_uploaded_file(dirty_image, tmpdir)
            
            # Валидируем изображения
            await validate_image(clean_path)
            await validate_image(dirty_path)
            
            # Выполняем анализ
            result = model.analyze_cleanliness(
                clean_image_path=clean_path,
                dirty_image_path=dirty_path,
                trace_id=trace_id,
                user_id=request.user_id
            )
            
            # Добавляем метаданные запроса
            result["request_metadata"] = {
                "user_id": request.user_id,
                "original_filenames": {
                    "clean": clean_image.filename,
                    "dirty": dirty_image.filename
                },
                "file_sizes": {
                    "clean": os.path.getsize(clean_path),
                    "dirty": os.path.getsize(dirty_path)
                }
            }
            
            # Формируем ответ
            response = CleanlinessAnalysisResponse(
                success=result["success"],
                trace_id=trace_id,
                result=result.get("parsed_response", {}),
                metrics=result.get("metrics", {}),
                model_info=result.get("model_info", {})
            )
            
            return response
            
        except ValueError as e:
            tracer.trace_error(
                trace_id=trace_id,
                name="validation_error",
                error=str(e),
                input_data={
                    "clean_filename": clean_image.filename,
                    "dirty_filename": dirty_image.filename,
                    "user_id": request.user_id
                },
                user_id=request.user_id
            )
            raise HTTPException(status_code=400, detail=str(e))
            
        except Exception as e:
            tracer.trace_error(
                trace_id=trace_id,
                name="analysis_error",
                error=str(e),
                input_data={
                    "clean_filename": clean_image.filename,
                    "dirty_filename": dirty_image.filename
                },
                user_id=request.user_id
            )
            raise HTTPException(status_code=500, detail=f"Ошибка анализа: {str(e)}")

@router.get("/health")
async def health_check():
    """Проверка здоровья AI сервиса"""
    try:
        is_healthy = model.check_ollama_health()
        
        if is_healthy:
            return {
                "status": "healthy",
                "model": model.model_name,
                "ollama_url": model.ollama_url
            }
        else:
            raise HTTPException(
                status_code=503,
                detail="Ollama недоступен или модель не загружена"
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics/{trace_id}")
async def get_trace_metrics(trace_id: str):
    """
    Получение метрик по trace_id
    
    - **trace_id**: ID трассировки для получения метрик
    """
    # В реальном приложении здесь можно получать метрики из Langfuse
    return {
        "trace_id": trace_id,
        "message": "Метрики доступны в Langfuse dashboard",
        "langfuse_url": f"https://cloud.langfuse.com/trace/{trace_id}"
    }