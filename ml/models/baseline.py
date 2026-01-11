# Добавить в импорты:
from ml.tracing.langfuse_config import tracer
import uuid


class LLavaBaselineModel:
    # ... существующий код ...

    def analyze_cleanliness(
            self,
            clean_image_path: str,
            dirty_image_path: str,
            trace_id: Optional[str] = None,
            user_id: Optional[str] = None
    ) -> Dict:
        """
        Анализирует чистоту квартиры по двум изображениям с трассировкой

        Args:
            clean_image_path: Путь к эталонному (чистому) изображению
            dirty_image_path: Путь к оцениваемому изображению
            trace_id: ID для трассировки (если None, генерируется автоматически)
            user_id: ID пользователя для трассировки

        Returns:
            Dict с результатами анализа
        """
        # Генерируем trace_id если не предоставлен
        if not trace_id:
            trace_id = str(uuid.uuid4())

        start_time = time.time()

        # Подготавливаем данные для трассировки
        trace_name = f"cleanliness_analysis_{time.strftime('%Y%m%d_%H%M%S')}"
        input_data = {
            "clean_image": clean_image_path,
            "dirty_image": dirty_image_path,
            "model": self.model_name,
            "prompt_length": len(self._build_prompt())
        }

        try:
            # Выполняем анализ
            result = self._perform_analysis(clean_image_path, dirty_image_path)

            # Рассчитываем метрики
            latency = time.time() - start_time
            result["metrics"]["latency"] = round(latency, 2)

            # Сохраняем трассировку
            tracer.trace_llm_call(
                trace_id=trace_id,
                name=trace_name,
                input_data=input_data,
                output_data=result,
                metadata={
                    "analysis_type": "cleanliness_assessment",
                    "image_count": 2,
                    "model": self.model_name
                },
                user_id=user_id
            )

            result["trace_id"] = trace_id
            return result

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Ошибка анализа: {error_msg}")

            # Трассируем ошибку
            tracer.trace_error(
                trace_id=trace_id,
                name=f"error_{trace_name}",
                error=error_msg,
                input_data=input_data,
                user_id=user_id
            )

            raise

    def _perform_analysis(self, clean_image_path: str, dirty_image_path: str) -> Dict:
        """Внутренний метод для выполнения анализа (вынесен для чистоты кода)"""
        # ... код из предыдущего метода analyze_cleanliness ...