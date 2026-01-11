import asyncio
import hashlib
import json
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import aiohttp
import orjson
import base64
import redis.asyncio as redis
from fastapi import HTTPException
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import logging
import gzip
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache

from backend.config import settings
from ml.tracing.langfuse_config import tracer

logger = logging.getLogger(__name__)

@dataclass
class ModelResponse:
    """Структурированный ответ модели"""
    success: bool
    defects: List[str]
    score: int
    recommendations: str
    raw_response: str
    metadata: Dict[str, Any]
    trace_id: Optional[str] = None

@dataclass
class ModelMetrics:
    """Метрики производительности модели"""
    inference_time: float
    token_count: int
    prompt_tokens: int
    completion_tokens: int
    cache_hit: bool = False

class LLMAsyncService:
    """Асинхронный сервис для работы с LLaVA моделью"""
    
    def __init__(self):
        self.ollama_url = settings.ollama_url
        self.model_name = settings.llava_model
        self.timeout = aiohttp.ClientTimeout(total=settings.request_timeout)
        self.redis_client = None
        self.thread_pool = ThreadPoolExecutor(max_workers=4)
        self._prompt_cache = {}
        
        # Промпты A/B вариантов
        self.prompt_variants = {
            "v1": self._build_prompt_v1,
            "v2": self._build_prompt_v2,
            "v3": self._build_prompt_v3,
        }
        
        # Статистика использования
        self.stats = {
            "total_requests": 0,
            "cache_hits": 0,
            "errors": 0,
            "avg_inference_time": 0
        }
        
        self._init_cache()
    
    async def _init_cache(self):
        """Инициализация кэша Redis"""
        try:
            self.redis_client = redis.Redis(
                host='localhost',
                port=6379,
                db=0,
                decode_responses=False,
                socket_keepalive=True
            )
            await self.redis_client.ping()
            logger.info("Redis cache initialized")
        except Exception as e:
            logger.warning(f"Redis not available, using in-memory cache: {e}")
            self.redis_client = None
    
    def _build_prompt_v1(self) -> str:
        """Базовый промпт"""
        return """Ты ассистент для оценки чистоты квартир. У тебя есть ДВЕ фотографии:
    — первое фото — чистая квартира (эталон);
    — второе фото — оцениваемая квартира.

    Если изображения по теме НЕ совпадают (например, одно не является квартирой или предметы/обстановка принципиально разные),
    отвечай строго так: "Недостатки: невозможно оценить — несоответствие изображений. Оценка: 0. Рекомендации: загрузите корректные фото."

    Если изображения совпадают по теме, внимательно сравни их и найди все различия, которые указывают на недостатки чистоты.

    Отвечай ТОЛЬКО по шаблону ниже, на русском языке, БЕЗ вступлений, пояснений и обращений.

    Формат ответа строго один:
    "Недостатки: [список через запятую].
    Оценка: [число от 1 до 10, где 10 - идеально чисто, 1 - очень грязно].
    Рекомендации: [конкретные рекомендации по уборке, не более 500 символов].""""
    
    def _build_prompt_v2(self) -> str:
        """Оптимизированный промпт с примерами"""
        return """Ты эксперт по уборке. Сравни две фотографии одной квартиры и оцени чистоту.

    СРАВНИВАЙ:
    ✓ Пыль на поверхностях (полки, столы, подоконники)
    ✓ Пятна на полу, мебели, стенах
    ✓ Беспорядок (разбросанные вещи, одежда)
    ✓ Грязную посуду, мусор
    ✓ Чистоту окон, зеркал, сантехники
    
    ЕСЛИ фото разные комнаты → "Недостатки: невозможно оценить — несоответствие изображений. Оценка: 0. Рекомендации: загрузите корректные фото."
    
    ФОРМАТ ОТВЕТА (только так):
    Недостатки: [список через запятую].
    Оценка: [1-10].
    Рекомендации: [краткие советы по уборке]."""
    
    def _build_prompt_v3(self) -> str:
        """Краткий промпт для быстрого ответа"""
        return """Оцени чистоту. Сравни 2 фото одной квартиры. Если разные комнаты → "Недостатки: невозможно оценить — несоответствие изображений. Оценка: 0. Рекомендации: загрузите корректные фото."

    Ответ строго в формате:
    Недостатки: [через запятую].
    Оценка: [1-10].
    Рекомендации: [до 100 символов]."""
    
    def _get_cache_key(self, clean_image: bytes, dirty_image: bytes, prompt_variant: str) -> str:
        """Генерирует ключ кэша для изображений"""
        # Создаем хэш из изображений и промпта
        content_hash = hashlib.sha256()
        content_hash.update(clean_image)
        content_hash.update(dirty_image)
        content_hash.update(prompt_variant.encode())
        return f"llava:{content_hash.hexdigest()}"
    
    async def _get_cached_response(self, cache_key: str) -> Optional[Dict]:
        """Получает ответ из кэша"""
        if not self.redis_client:
            return None
        
        try:
            cached = await self.redis_client.get(cache_key)
            if cached:
                self.stats["cache_hits"] += 1
                return orjson.loads(gzip.decompress(cached))
        except Exception as e:
            logger.warning(f"Cache read error: {e}")
        
        return None
    
    async def _set_cached_response(self, cache_key: str, response: Dict, ttl: int = 3600):
        """Сохраняет ответ в кэш"""
        if not self.redis_client:
            return
        
        try:
            compressed = gzip.compress(orjson.dumps(response))
            await self.redis_client.setex(cache_key, ttl, compressed)
        except Exception as e:
            logger.warning(f"Cache write error: {e}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((aiohttp.ClientError, asyncio.TimeoutError))
    )
    async def _call_ollama_api(
        self, 
        session: aiohttp.ClientSession,
        prompt: str,
        images: List[str],
        prompt_variant: str = "v1"
    ) -> Dict:
        """Асинхронный вызов Ollama API"""
        data = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "images": images,
            "options": {
                "temperature": 0.1,
                "top_p": 0.9,
                "num_predict": 800 if prompt_variant == "v3" else 1200
            }
        }
        
        async with session.post(
            f"{self.ollama_url}/api/generate",
            json=data,
            timeout=self.timeout
        ) as response:
            response.raise_for_status()
            return await response.json()
    
    async def analyze_cleanliness(
        self,
        clean_image_path: str,
        dirty_image_path: str,
        prompt_variant: str = "v1",
        use_cache: bool = True,
        user_id: Optional[str] = None,
        trace_id: Optional[str] = None
    ) -> Tuple[ModelResponse, ModelMetrics]:
        """
        Асинхронный анализ чистоты квартиры
        
        Args:
            clean_image_path: Путь к чистому изображению
            dirty_image_path: Путь к оцениваемому изображению
            prompt_variant: Версия промпта (v1, v2, v3)
            use_cache: Использовать кэш
            user_id: ID пользователя
            trace_id: ID трассировки
            
        Returns:
            Кортеж (ModelResponse, ModelMetrics)
        """
        start_time = time.time()
        self.stats["total_requests"] += 1
        
        try:
            # Чтение и кодирование изображений
            loop = asyncio.get_event_loop()
            clean_image, dirty_image = await asyncio.gather(
                loop.run_in_executor(self.thread_pool, self._read_and_encode, clean_image_path),
                loop.run_in_executor(self.thread_pool, self._read_and_encode, dirty_image_path)
            )
            
            # Проверка кэша
            cache_hit = False
            if use_cache:
                cache_key = self._get_cache_key(clean_image, dirty_image, prompt_variant)
                cached_result = await self._get_cached_response(cache_key)
                
                if cached_result:
                    cache_hit = True
                    metrics = ModelMetrics(
                        inference_time=time.time() - start_time,
                        token_count=cached_result.get("eval_count", 0),
                        prompt_tokens=cached_result.get("prompt_eval_count", 0),
                        completion_tokens=cached_result.get("eval_count", 0),
                        cache_hit=True
                    )
                    
                    response = ModelResponse(
                        success=True,
                        defects=cached_result.get("defects", []),
                        score=cached_result.get("score", 0),
                        recommendations=cached_result.get("recommendations", ""),
                        raw_response=cached_result.get("raw_response", ""),
                        metadata={
                            "prompt_variant": prompt_variant,
                            "cached": True
                        },
                        trace_id=trace_id
                    )
                    
                    return response, metrics
            
            # Выбор промпта
            prompt_func = self.prompt_variants.get(prompt_variant, self._build_prompt_v1)
            prompt = prompt_func()
            
            # Вызов модели
            async with aiohttp.ClientSession() as session:
                result = await self._call_ollama_api(
                    session=session,
                    prompt=prompt,
                    images=[
                        base64.b64encode(clean_image).decode('utf-8'),
                        base64.b64encode(dirty_image).decode('utf-8')
                    ],
                    prompt_variant=prompt_variant
                )
            
            # Парсинг ответа
            raw_response = result.get("response", "").strip()
            parsed_response = await self._parse_response_async(raw_response)
            
            # Подготовка ответа
            response = ModelResponse(
                success=True,
                defects=parsed_response["defects"],
                score=parsed_response["score"],
                recommendations=parsed_response["recommendations"],
                raw_response=raw_response,
                metadata={
                    "prompt_variant": prompt_variant,
                    "cached": False,
                    "model": self.model_name
                },
                trace_id=trace_id
            )
            
            # Расчет метрик
            inference_time = time.time() - start_time
            metrics = ModelMetrics(
                inference_time=inference_time,
                token_count=result.get("eval_count", 0) + result.get("prompt_eval_count", 0),
                prompt_tokens=result.get("prompt_eval_count", 0),
                completion_tokens=result.get("eval_count", 0),
                cache_hit=cache_hit
            )
            
            # Обновление статистики
            self.stats["avg_inference_time"] = (
                (self.stats["avg_inference_time"] * (self.stats["total_requests"] - 1) + inference_time) 
                / self.stats["total_requests"]
            )
            
            # Кэширование результата
            if use_cache and not cache_hit:
                cache_key = self._get_cache_key(clean_image, dirty_image, prompt_variant)
                cache_data = {
                    "defects": response.defects,
                    "score": response.score,
                    "recommendations": response.recommendations,
                    "raw_response": response.raw_response,
                    "eval_count": result.get("eval_count", 0),
                    "prompt_eval_count": result.get("prompt_eval_count", 0)
                }
                await self._set_cached_response(cache_key, cache_data)
            
            # Трассировка
            if trace_id:
                tracer.trace_llm_call(
                    trace_id=trace_id,
                    name=f"async_analysis_{prompt_variant}",
                    input_data={
                        "prompt_variant": prompt_variant,
                        "use_cache": use_cache,
                        "image_sizes": {
                            "clean": len(clean_image),
                            "dirty": len(dirty_image)
                        }
                    },
                    output_data={
                        "response": response,
                        "metrics": metrics.__dict__
                    },
                    user_id=user_id
                )
            
            return response, metrics
            
        except Exception as e:
            self.stats["errors"] += 1
            logger.error(f"Analysis error: {e}")
            
            if trace_id:
                tracer.trace_error(
                    trace_id=trace_id,
                    name="async_analysis_error",
                    error=str(e),
                    input_data={
                        "clean_image": clean_image_path,
                        "dirty_image": dirty_image_path,
                        "prompt_variant": prompt_variant
                    },
                    user_id=user_id
                )
            
            raise HTTPException(
                status_code=500,
                detail=f"Analysis failed: {str(e)}"
            )
    
    def _read_and_encode(self, image_path: str) -> bytes:
        """Чтение изображения в байтах"""
        with open(image_path, "rb") as f:
            return f.read()
    
    async def _parse_response_async(self, response: str) -> Dict:
        """Асинхронный парсинг ответа модели"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.thread_pool,
            self._parse_response,
            response
        )
    
    def _parse_response(self, response: str) -> Dict:
        """Синхронный парсинг ответа"""
        import re
        
        result = {
            "defects": [],
            "score": 0,
            "recommendations": ""
        }
        
        try:
            # Несоответствие изображений
            if "невозможно оценить" in response or "несоответствие изображений" in response:
                result["defects"] = ["Несоответствие изображений"]
                result["score"] = 0
                result["recommendations"] = "Загрузите корректные фото одной и той же квартиры"
                return result
            
            # Парсинг недостатков
            if "Недостатки:" in response:
                lines = response.split('\n')
                for i, line in enumerate(lines):
                    if line.strip().startswith("Недостатки:"):
                        defects_text = line[len("Недостатки:"):].strip()
                        # Ищем до следующего заголовка или конца
                        for j in range(i + 1, len(lines)):
                            if lines[j].strip().startswith("Оценка:"):
                                break
                            defects_text += " " + lines[j].strip()
                        
                        # Очистка и разбиение
                        defects_text = defects_text.rstrip('.').strip()
                        defects = re.split(r'[,;]', defects_text)
                        result["defects"] = [d.strip() for d in defects if d.strip()]
                        break
            
            # Парсинг оценки
            if "Оценка:" in response:
                score_match = re.search(r'Оценка:\s*(\d{1,2})', response)
                if score_match:
                    score = int(score_match.group(1))
                    if 0 <= score <= 10:
                        result["score"] = score
            
            # Парсинг рекомендаций
            if "Рекомендации:" in response:
                rec_start = response.find("Рекомендации:") + len("Рекомендации:")
                rec_text = response[rec_start:].strip()
                # Убираем возможные следующие заголовки
                for marker in ["Недостатки:", "Оценка:", "Рекомендации:"]:
                    if marker in rec_text:
                        rec_text = rec_text.split(marker)[0]
                
                result["recommendations"] = rec_text[:500].strip()
            
        except Exception as e:
            logger.error(f"Parse error: {e}")
        
        return result
    
    async def get_service_stats(self) -> Dict:
        """Получение статистики сервиса"""
        return {
            **self.stats,
            "timestamp": datetime.now().isoformat(),
            "cache_enabled": self.redis_client is not None,
            "active_threads": self.thread_pool._max_workers,
            "prompt_variants": list(self.prompt_variants.keys())
        }
    
    async def cleanup(self):
        """Очистка ресурсов"""
        self.thread_pool.shutdown(wait=True)
        if self.redis_client:
            await self.redis_client.close()

# Глобальный инстанс сервиса
_service_instance = None

async def get_llm_service() -> LLMAsyncService:
    """Фабрика для получения сервиса LLM (для dependency injection)"""
    global _service_instance
    if _service_instance is None:
        _service_instance = LLMAsyncService()
    return _service_instance