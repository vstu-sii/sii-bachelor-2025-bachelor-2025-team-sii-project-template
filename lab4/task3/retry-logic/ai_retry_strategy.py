"""
Стратегия повторных попыток для AI запросов.
"""
import asyncio
import logging
from typing import Callable, Type, Optional, Any, Dict
from datetime import datetime, timedelta
from functools import wraps
import random

from ..backend_exceptions.custom_exceptions.business import (
    AIAnalysisFailedException,
    ExternalServiceException
)

logger = logging.getLogger(__name__)

class RetryStrategy:
    """Стратегия повторных попыток для внешних вызовов."""
    
    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 30.0,
        backoff_factor: float = 2.0,
        jitter: bool = True,
        retry_on_exceptions: tuple = None
    ):
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.jitter = jitter
        self.retry_on_exceptions = retry_on_exceptions or (
            ConnectionError,
            TimeoutError,
            ExternalServiceException,
            AIAnalysisFailedException
        )
    
    def __call__(self, func: Callable) -> Callable:
        """Декоратор для применения стратегии повторных попыток."""
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            total_attempts = self.max_retries + 1  # +1 для первоначальной попытки
            
            for attempt in range(total_attempts):
                try:
                    if attempt > 0:
                        logger.info(f"Попытка {attempt + 1}/{total_attempts} для {func.__name__}")
                    
                    return await func(*args, **kwargs)
                    
                except self.retry_on_exceptions as exc:
                    last_exception = exc
                    
                    # Проверяем, стоит ли повторять
                    if not self._should_retry(attempt, exc):
                        logger.warning(f"Прекращение повторных попыток для {func.__name__}")
                        raise
                    
                    # Рассчитываем задержку
                    delay = self._calculate_delay(attempt)
                    
                    # Добавляем jitter для равномерного распределения нагрузки
                    if self.jitter:
                        delay = self._add_jitter(delay)
                    
                    logger.warning(
                        f"Ошибка в {func.__name__} (попытка {attempt + 1}/{total_attempts}): "
                        f"{exc}. Повтор через {delay:.2f}с"
                    )
                    
                    # Ждём перед следующей попыткой
                    await asyncio.sleep(delay)
                    
                except Exception as exc:
                    # Не повторяем для других исключений
                    logger.error(f"Критическая ошибка в {func.__name__}: {exc}")
                    raise
            
            # Если все попытки исчерпаны
            if last_exception:
                logger.error(
                    f"Все {total_attempts} попыток для {func.__name__} завершились ошибкой"
                )
                raise AIAnalysisFailedException(
                    f"Не удалось выполнить операцию после {total_attempts} попыток"
                ) from last_exception
        
        return wrapper
    
    def _should_retry(self, attempt: int, exception: Exception) -> bool:
        """Определяет, стоит ли повторять попытку."""
        if attempt >= self.max_retries:
            return False
        
        # Не повторяем для определенных типов ошибок
        if isinstance(exception, AIAnalysisFailedException):
            # Проверяем, является ли это временной ошибкой
            error_message = str(exception).lower()
            temporary_errors = [
                "timeout", "перегрузка", "overloaded", "rate limit",
                "временно недоступен", "service unavailable"
            ]
            
            if not any(keyword in error_message for keyword in temporary_errors):
                return False
        
        return True
    
    def _calculate_delay(self, attempt: int) -> float:
        """Рассчитывает задержку перед следующей попыткой."""
        delay = self.initial_delay * (self.backoff_factor ** attempt)
        return min(delay, self.max_delay)
    
    def _add_jitter(self, delay: float) -> float:
        """Добавляет случайную составляющую к задержке."""
        jitter_amount = delay * 0.1  # 10% jitter
        return delay + random.uniform(-jitter_amount, jitter_amount)

class CircuitBreaker:
    """Реализация паттерна Circuit Breaker."""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 30,
        half_open_max_attempts: int = 3
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_attempts = half_open_max_attempts
        
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.failure_count = 0
        self.last_failure_time = None
        self.half_open_attempts = 0
    
    async def execute(self, func: Callable, *args, **kwargs) -> Any:
        """Выполняет функцию с учетом состояния circuit breaker."""
        
        if self.state == "OPEN":
            # Проверяем, можно ли перейти в HALF_OPEN
            if self._can_move_to_half_open():
                self.state = "HALF_OPEN"
                self.half_open_attempts = 0
            else:
                raise ExternalServiceException("Сервис временно недоступен")
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
            
        except Exception as exc:
            self._on_failure()
            raise
    
    def _can_move_to_half_open(self) -> bool:
        """Проверяет, можно ли перейти в состояние HALF_OPEN."""
        if self.state != "OPEN" or not self.last_failure_time:
            return False
        
        time_since_failure = (datetime.now() - self.last_failure_time).total_seconds()
        return time_since_failure >= self.recovery_timeout
    
    def _on_success(self):
        """Обработка успешного выполнения."""
        if self.state == "HALF_OPEN":
            self.half_open_attempts += 1
            
            if self.half_open_attempts >= self.half_open_max_attempts:
                # Успешные попытки в HALF_OPEN, возвращаемся в CLOSED
                self.state = "CLOSED"
                self.failure_count = 0
                self.half_open_attempts = 0
                logger.info("Circuit breaker: CLOSED (recovered)")
        
        elif self.state == "CLOSED":
            # Сбрасываем счетчик ошибок при успехе
            self.failure_count = max(0, self.failure_count - 1)
    
    def _on_failure(self):
        """Обработка ошибки выполнения."""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.state == "HALF_OPEN":
            # Неудача в HALF_OPEN, возвращаемся в OPEN
            self.state = "OPEN"
            self.half_open_attempts = 0
            logger.warning("Circuit breaker: OPEN (half-open failed)")
        
        elif self.state == "CLOSED" and self.failure_count >= self.failure_threshold:
            # Превышен порог ошибок, переходим в OPEN
            self.state = "OPEN"
            logger.warning(f"Circuit breaker: OPEN (failure threshold reached: {self.failure_count})")

# Глобальные экземпляры стратегий
ai_retry_strategy = RetryStrategy(
    max_retries=3,
    initial_delay=2.0,
    max_delay=60.0,
    backoff_factor=1.5,
    jitter=True
)

ai_circuit_breaker = CircuitBreaker(
    failure_threshold=5,
    recovery_timeout=60,
    half_open_max_attempts=2
)

def with_ai_retry(func: Callable) -> Callable:
    """Декоратор для применения стратегии повторных попыток к AI функциям."""
    retry_decorator = ai_retry_strategy(func)
    
    @wraps(func)
    async def wrapper(*args, **kwargs):
        return await ai_circuit_breaker.execute(retry_decorator, *args, **kwargs)
    
    return wrapper

class AIMonitoring:
    """Мониторинг состояния AI сервиса."""
    
    def __init__(self):
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "retry_count": 0,
            "circuit_state": "CLOSED",
            "last_failure": None,
            "average_response_time": 0.0
        }
        self.response_times = []
    
    def record_request(self):
        """Запись нового запроса."""
        self.stats["total_requests"] += 1
    
    def record_success(self, response_time: float):
        """Запись успешного запроса."""
        self.stats["successful_requests"] += 1
        self.response_times.append(response_time)
        
        # Обновляем среднее время ответа
        if len(self.response_times) > 100:  # Ограничиваем историю
            self.response_times.pop(0)
        
        self.stats["average_response_time"] = sum(self.response_times) / len(self.response_times)
    
    def record_failure(self, error: Exception):
        """Запись неудачного запроса."""
        self.stats["failed_requests"] += 1
        self.stats["last_failure"] = datetime.now().isoformat()
    
    def record_retry(self):
        """Запись повторной попытки."""
        self.stats["retry_count"] += 1
    
    def update_circuit_state(self, state: str):
        """Обновление состояния circuit breaker."""
        self.stats["circuit_state"] = state
    
    def get_health_status(self) -> Dict[str, Any]:
        """Получение статуса здоровья AI сервиса."""
        success_rate = 0
        if self.stats["total_requests"] > 0:
            success_rate = (self.stats["successful_requests"] / self.stats["total_requests"]) * 100
        
        return {
            "is_healthy": success_rate > 95 and self.stats["circuit_state"] == "CLOSED",
            "success_rate": round(success_rate, 2),
            "circuit_state": self.stats["circuit_state"],
            "total_requests": self.stats["total_requests"],
            "failed_requests": self.stats["failed_requests"],
            "retry_count": self.stats["retry_count"],
            "average_response_time": round(self.stats["average_response_time"], 3),
            "last_failure": self.stats["last_failure"]
        }

# Глобальный экземпляр мониторинга
ai_monitoring = AIMonitoring()

def monitored_ai_call(func: Callable) -> Callable:
    """Декоратор для мониторинга AI вызовов."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        import time
        
        ai_monitoring.record_request()
        start_time = time.time()
        
        try:
            result = await func(*args, **kwargs)
            
            response_time = time.time() - start_time
            ai_monitoring.record_success(response_time)
            
            return result
            
        except Exception as exc:
            ai_monitoring.record_failure(exc)
            raise
    
    return wrapper

# Комбинированный декоратор для AI функций
def resilient_ai_function(func: Callable) -> Callable:
    """Комбинированный декоратор для AI функций с retry, circuit breaker и мониторингом."""
    return with_ai_retry(monitored_ai_call(func))
