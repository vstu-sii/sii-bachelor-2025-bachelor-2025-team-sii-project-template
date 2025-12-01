import torch
from PIL import Image
from transformers import AutoModelForCausalLM, AutoTokenizer
from qwen_vl_utils import process_vision_info
import gradio as gr
import os
from datetime import datetime

class CleaningEvaluator:
    def __init__(self, model_path="Qwen/Qwen-VL-Chat"):
        """
        Инициализация модели для оценки уборки
        
        Args:
            model_path: путь к модели Qwen-VL
        """
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Используется устройство: {self.device}")
        
        # Загрузка модели и токенизатора
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_path, 
            trust_remote_code=True
        )
        self.model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            device_map="auto" if self.device == "cuda" else None,
            trust_remote_code=True
        ).to(self.device)
        
        # Системный промпт для оценки уборки
        self.cleaning_system_prompt = """Ты - эксперт по оценке качества уборки помещений. 
        Тебе будут предоставлены два изображения: ДО уборки и ПОСЛЕ уборки.
        
        Проанализируй изображения и оцени:
        1. Общее улучшение чистоты
        2. Качество уборки разных зон (пол, поверхности, окна и т.д.)
        3. Заметность изменений
        4. Детали уборки
        
        Дай оценку от 1 до 10, где:
        1-3: Плохая уборка, минимальные изменения
        4-5: Удовлетворительно, заметны некоторые улучшения
        6-7: Хорошая уборка, значительные улучшения
        8-9: Отличная уборка, почти идеально
        10: Идеальная уборка
        
        Также предоставь развернутое описание изменений и рекомендации по улучшению."""

    def preprocess_images(self, before_image, after_image):
        """Предобработка изображений"""
        # Конвертируем в RGB если нужно
        if before_image.mode != 'RGB':
            before_image = before_image.convert('RGB')
        if after_image.mode != 'RGB':
            after_image = after_image.convert('RGB')
        
        # Сохраняем временные файлы для модели
        before_path = "temp_before.jpg"
        after_path = "temp_after.jpg"
        before_image.save(before_path)
        after_image.save(after_path)
        
        return before_path, after_path

    def evaluate_cleaning(self, before_image, after_image):
        """
        Основная функция оценки уборки
        
        Args:
            before_image: изображение ДО уборки
            after_image: изображение ПОСЛЕ уборки
            
        Returns:
            dict: результаты оценки
        """
        try:
            # Предобработка изображений
            before_path, after_path = self.preprocess_images(before_image, after_image)
            
            # Формируем запрос для модели
            query = [
                {
                    "image": before_path,
                },
                {
                    "image": after_path,
                },
                {
                    "text": f"{self.cleaning_system_prompt}\n\n"
                    "Пожалуйста, проанализируй эти два изображения (ДО и ПОСЛЕ уборки) "
                    "и дай детальную оценку качества уборки. "
                    "Обязательно укажи итоговую оценку числом от 1 до 10."
                }
            ]
            
            # Подготавливаем контекст
            text = self.tokenizer.from_list_format(query)
            
            # Генерируем ответ
            with torch.no_grad():
                response, _ = self.model.chat(
                    self.tokenizer,
                    query=text,
                    history=None,
                    system="Ты помощник по оценке качества уборки."
                )
            
            # Извлекаем оценку из ответа
            score = self.extract_score(response)
            
            # Формируем результат
            result = {
                'score': score,
                'detailed_analysis': response,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'improvement': self.assess_improvement(score)
            }
            
            # Очистка временных файлов
            os.remove(before_path)
            os.remove(after_path)
            
            return result
            
        except Exception as e:
            return {
                'error': str(e),
                'score': 0,
                'detailed_analysis': f"Ошибка при обработке: {str(e)}"
            }

    def extract_score(self, response):
        """Извлекает числовую оценку из текстового ответа"""
        import re
        
        # Ищем числа от 1 до 10 в тексте
        scores = re.findall(r'\b(10|[1-9])\b', response)
        
        if scores:
            # Берем первое найденное число
            try:
                return int(scores[0])
            except:
                pass
        
        # Если не нашли число, пытаемся определить по контексту
        if any(word in response.lower() for word in ['отлично', 'превосходно', 'идеально']):
            return 9
        elif any(word in response.lower() for word in ['хорошо', 'качественно']):
            return 7
        elif any(word in response.lower() for word in ['удовлетворительно', 'нормально']):
            return 5
        elif any(word in response.lower() for word in ['плохо', 'неудовлетворительно']):
            return 3
        
        return 5  # Средняя оценка по умолчанию

    def assess_improvement(self, score):
        """Оценивает уровень улучшения на основе оценки"""
        if score >= 9:
            return "Выдающееся улучшение"
        elif score >= 7:
            return "Значительное улучшение"
        elif score >= 5:
            return "Заметное улучшение"
        elif score >= 3:
            return "Минимальное улучшение"
        else:
            return "Незначительное улучшение"

def create_gradio_interface():
    """Создание Gradio интерфейса"""
    
    # Инициализация оценщика
    evaluator = CleaningEvaluator()
    
    def process_images(before_img, after_img):
        """Обработка изображений через Gradio"""
        if before_img is None or after_img is None:
            return "Пожалуйста, загрузите оба изображения", 0, ""
        
        result = evaluator.evaluate_cleaning(before_img, after_img)
        
        if 'error' in result:
            return f"Ошибка: {result['error']}", 0, ""
        
        # Форматируем вывод
        analysis = f"""
        ## 📊 Оценка уборки: {result['score']}/10
        ### Уровень улучшения: {result['improvement']}
        
        ### Детальный анализ:
        {result['detailed_analysis']}
        
        *Время оценки: {result['timestamp']}*
        """
        
        return analysis, result['score'], result['detailed_analysis']
    
    # Создание интерфейса
    with gr.Blocks(title="Оценка качества уборки", theme=gr.themes.Soft()) as demo:
        gr.Markdown("# 🧹 Оценка качества уборки помещения")
        gr.Markdown("Загрузите два изображения: **ДО** и **ПОСЛЕ** уборки")
        
        with gr.Row():
            with gr.Column():
                before_image = gr.Image(
                    label="Фото ДО уборки",
                    type="pil",
                    height=300
                )
                gr.Markdown("### 📸 До уборки")
            
            with gr.Column():
                after_image = gr.Image(
                    label="Фото ПОСЛЕ уборки",
                    type="pil",
                    height=300
                )
                gr.Markdown("### ✅ После уборки")
        
        with gr.Row():
            evaluate_btn = gr.Button("Оценить уборку", variant="primary", size="lg")
        
        with gr.Row():
            with gr.Column():
                score_display = gr.Label(label="Итоговая оценка")
                score_gauge = gr.Slider(
                    minimum=0,
                    maximum=10,
                    label="Оценка (1-10)",
                    interactive=False
                )
        
        with gr.Row():
            analysis_output = gr.Markdown(label="Детальный анализ")
        
        with gr.Row():
            detailed_output = gr.Textbox(
                label="Полный отчет",
                lines=10,
                max_lines=20
            )
        
        # Обработка нажатия кнопки
        evaluate_btn.click(
            fn=process_images,
            inputs=[before_image, after_image],
            outputs=[analysis_output, score_gauge, detailed_output]
        )
        
        gr.Markdown("---")
        gr.Markdown("### ℹ️ Как это работает:")
        gr.Markdown("""
        1. Загрузите фото помещения **ДО** уборки
        2. Загрузите фото помещения **ПОСЛЕ** уборки
        3. Нажмите кнопку "Оценить уборку"
        4. Получите оценку от 1 до 10 и детальный анализ
        
        **Модель анализирует:**
        - Общую чистоту
        - Качество уборки поверхностей
        - Организацию предметов
        - Заметность изменений
        """)
    
    return demo

def main():
    """Основная функция"""
    print("🚀 Запуск системы оценки уборки...")
    
    # Создаем и запускаем интерфейс
    demo = create_gradio_interface()
    
    # Запускаем Gradio интерфейс
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=True
    )

if __name__ == "__main__":
    main()
