from langfuse import Langfuse
from langfuse.model import CreateTrace, CreateGeneration, CreateSpan
from typing import Dict, Optional, Any
import time
from backend.config import settings
import logging

logger = logging.getLogger(__name__)


class LangfuseTracer:
    """Класс для трассировки LLM вызовов через Langfuse"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LangfuseTracer, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Инициализирует клиент Langfuse"""
        try:
            if all([
                settings.langfuse_secret_key,
                settings.langfuse_public_key,
                settings.langfuse_host
            ]):
                self.langfuse = Langfuse(
                    secret_key=settings.langfuse_secret_key,
                    public_key=settings.langfuse_public_key,
                    host=settings.langfuse_host,
                )
                self.enabled = True
                logger.info("Langfuse tracer инициализирован")
            else:
                self.langfuse = None
                self.enabled = False
                logger.warning("Langfuse не настроен. Проверьте переменные окружения.")

        except Exception as e:
            logger.error(f"Ошибка при инициализации Langfuse: {e}")
            self.langfuse = None
            self.enabled = False

    def trace_llm_call(
            self,
            trace_id: str,
            name: str,
            input_data: Dict,
            output_data: Dict,
            metadata: Optional[Dict] = None,
            user_id: Optional[str] = None
    ) -> None:
        """
        Создает трассировку для LLM вызова

        Args:
            trace_id: Уникальный ID трассировки
            name: Название трассировки
            input_data: Входные данные
            output_data: Выходные данные
            metadata: Дополнительные метаданные
            user_id: ID пользователя
        """
        if not self.enabled:
            return

        try:
            # Создаем трассировку
            trace = self.langfuse.trace(
                CreateTrace(
                    id=trace_id,
                    name=name,
                    user_id=user_id,
                    metadata=metadata or {},
                )
            )

            # Создаем спан для LLM вызова
            generation = trace.generation(
                CreateGeneration(
                    name="LLaVA Cleanliness Analysis",
                    model=output_data.get("model_info", {}).get("model", "unknown"),
                    input=input_data,
                    output=output_data,
                    metadata={
                                 **metadata or {},
                    "latency": output_data.get("metrics", {}).get("latency", 0),
            "token_count": output_data.get("metrics", {}).get("token_count", 0),
            "defects_count": len(output_data.get("parsed_response", {}).get("defects", [])),
            "score": output_data.get("parsed_response", {}).get("score", 0)
            }
            )
            )

            # Добавляем промпт как отдельный спан
            trace.span(
                CreateSpan(
                    name="Prompt Engineering",
                    input={"prompt": input_data.get("prompt", "")},
                    metadata={
                        "prompt_length": len(input_data.get("prompt", "")),
                        "images_count": len(input_data.get("images", []))
                    }
                )
            )

            # Закрываем трассировку
            trace.update(end_time=time.time())

            logger.debug(f"Трассировка сохранена в Langfuse: {trace_id}")

        except Exception as e:
            logger.error(f"Ошибка при сохранении трассировки в Langfuse: {e}")

    def trace_error(
            self,
            trace_id: str,
            name: str,
            error: str,
            input_data: Dict,
            metadata: Optional[Dict] = None,
            user_id: Optional[str] = None
    ) -> None:
        """Создает трассировку для ошибки"""
        if not self.enabled:
            return

        try:
            trace = self.langfuse.trace(
                CreateTrace(
                    id=trace_id,
                    name=name,
                    user_id=user_id,
                    metadata={
                        **(metadata or {}),
                        "error": True,
                        "error_message": error
                    },
                )
            )

            trace.span(
                CreateSpan(
                    name="Error",
                    input=input_data,
                    output={"error": error},
                    level="ERROR"
                )
            )

            trace.update(end_time=time.time())

        except Exception as e:
            logger.error(f"Ошибка при сохранении трассировки ошибки: {e}")

    def flush(self):
        """Отправляет все ожидающие события"""
        if self.enabled and self.langfuse:
            try:
                self.langfuse.flush()
            except Exception as e:
                logger.error(f"Ошибка при отправке событий в Langfuse: {e}")


# Синглтон инстанс
tracer = LangfuseTracer()