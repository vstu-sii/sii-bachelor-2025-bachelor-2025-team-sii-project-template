import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from PIL import Image
import gradio as gr
import os
from typing import Dict, Tuple, Optional
import json

class CleaningAssessmentModel:
    def __init__(self, model_name: str = "Qwen/Qwen-VL-Chat"):
        """
        Инициализация модели Qwen-VL для оценки уборки
        
        Args:
            model_name: название модели на HuggingFace
        """
        print(f"Загрузка модели {model_name}...")
        
        # Загружаем токенизатор и модель
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name, 
            trust_remote_code=True
        )
        
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto" if torch.cuda.is_available() else "cpu",
            trust_remote_code=True
        ).eval()
        
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Модель загружена на устройство: {self.device}")
        
        # Критерии оценки уборки
        self.cleaning_criteria = {
            "полы": ["чистый пол", "отсутствие мусора", "отсутствие пятен"],
            "поверхности": ["протертые поверхности", "отсутствие пыли", "чистые столы"],
            "мебель": ["расставленная мебель", "чистая мебель", "отсутствие вещей"],
            "техника": ["чистая техника", "исправное состояние"],
            "стены": ["чистые стены", "отсутствие пятен"],
            "окна": ["чистые окна", "чистые подоконники"],
            "ванная/туалет": ["чистые сантехника", "отсутствие известкового налета"],
            "кухня": ["чистая плита", "чистая раковина", "чистые шкафы"]
        }
    
    def prepare_images(self, before_image_path: str, after_image_path: str) -> Tuple[str, str]:
        """
        Подготовка изображений для модели
        
        Args:
            before_image_path: путь к изображению до уборки
            after_image_path: путь к изображению после уборки
            
        Returns:
            Кортеж с обработанными изображениями
        """
        try:
            # Открываем и проверяем изображения
            before_img = Image.open(before_image_path).convert('RGB')
            after_img = Image.open(after_image_path).convert('RGB')
            
            # Ресайз для экономии памяти (опционально)
            max_size = (512, 512)
            before_img.thumbnail(max_size, Image.Resampling.LANCZOS)
            after_img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Сохраняем временные файлы
            before_img.save("temp_before.jpg")
            after_img.save("temp_after.jpg")
            
            return "temp_before.jpg", "temp_after.jpg"
            
        except Exception as e:
            raise ValueError(f"Ошибка обработки изображений: {e}")
    
    def generate_assessment_prompt(self) -> str:
        """
        Генерация промпта для оценки уборки
        
        Returns:
            Промпт для модели
        """
        criteria_text = "\n".join([
            f"- {category}: {', '.join(criteria)}"
            for category, criteria in self.cleaning_criteria.items()
        ])
        
        prompt = f"""Ты - профессиональный оценщик чистоты помещений. Тебе будут представлены два изображения одного помещения: до уборки и после уборки.

Пожалуйста, проанализируй эти изображения и оцени качество уборки по следующим критериям:

{criteria_text}

Проанализируй изображения и предоставь оценку в следующем JSON формате:
{{
    "overall_score": 0-100,
    "detailed_scores": {{
        "floors": 0-100,
        "surfaces": 0-100,
        "furniture": 0-100,
        "appliances": 0-100,
        "walls": 0-100,
        "windows": 0-100,
        "bathroom": 0-100,
        "kitchen": 0-100
    }},
    "improvements": ["список улучшений"],
    "issues": ["список проблем"],
    "recommendations": ["рекомендации по улучшению"],
    "verdict": "принято/не принято"
}}

Оцени объективно и учитывай разницу между двумя изображениями. Убедись, что ответ содержит только JSON без дополнительного текста."""
        
        return prompt
    
    def assess_cleaning(self, before_image_path: str, after_image_path: str) -> Dict:
        """
        Основная функция оценки уборки
        
        Args:
            before_image_path: путь к изображению до уборки
            after_image_path: путь к изображению после уборки
            
        Returns:
            Словарь с результатами оценки
        """
        try:
            # Подготавливаем изображения
            before_img, after_img = self.prepare_images(before_image_path, after_image_path)
            
            # Генерируем промпт
            prompt = self.generate_assessment_prompt()
            
            # Формируем запрос для Qwen-VL
            query = self.tokenizer.from_list_format([
                {'image': before_img},
                {'image': after_img},
                {'text': prompt}
            ])
            
            # Генерируем ответ
            with torch.no_grad():
                response, _ = self.model.chat(
                    self.tokenizer,
                    query=query,
                    history=None,
                    max_new_tokens=1024
                )
            
            # Парсим JSON ответ
            try:
                # Ищем JSON в ответе
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                
                if json_start != -1 and json_end != 0:
                    json_str = response[json_start:json_end]
                    result = json.loads(json_str)
                else:
                    # Если JSON не найден, создаем структуру вручную
                    result = {
                        "overall_score": 0,
                        "detailed_scores": {},
                        "improvements": [],
                        "issues": ["Ошибка парсинга ответа модели"],
                        "recommendations": ["Проверьте входные данные"],
                        "verdict": "не принято"
                    }
                
                # Добавляем сырой ответ модели
                result["raw_response"] = response
                
                return result
                
            except json.JSONDecodeError as e:
                print(f"Ошибка парсинга JSON: {e}")
                return {
                    "error": "Ошибка парсинка ответа модели",
                    "raw_response": response,
                    "overall_score": 0,
                    "verdict": "не принято"
                }
            
        except Exception as e:
            print(f"Ошибка при оценке: {e}")
            return {
                "error": str(e),
                "overall_score": 0,
                "verdict": "не принято"
            }
    
    def visualize_results(self, results: Dict, before_img: Image, after_img: Image) -> Dict:
        """
        Визуализация результатов оценки
        
        Args:
            results: результаты оценки
            before_img: изображение до
            after_img: изображение после
            
        Returns:
            Словарь с визуализированными результатами
        """
        # Создаем текстовое представление
        text_output = f"""
        ## Результаты оценки уборки
        
        ### Общая оценка: {results.get('overall_score', 0)}/100
        ### Вердикт: {results.get('verdict', 'не определено')}
        
        ### Детальные оценки:
        """
        
        detailed = results.get('detailed_scores', {})
        for category, score in detailed.items():
            category_ru = {
                'floors': 'Полы',
                'surfaces': 'Поверхности',
                'furniture': 'Мебель',
                'appliances': 'Техника',
                'walls': 'Стены',
                'windows': 'Окна',
                'bathroom': 'Ванная/Туалет',
                'kitchen': 'Кухня'
            }.get(category, category)
            
            text_output += f"\n- {category_ru}: {score}/100"
        
        if 'improvements' in results and results['improvements']:
            text_output += f"\n\n### Улучшения:\n" + "\n".join([f"- {imp}" for imp in results['improvements']])
        
        if 'issues' in results and results['issues']:
            text_output += f"\n\n### Проблемы:\n" + "\n".join([f"- {issue}" for issue in results['issues']])
        
        if 'recommendations' in results and results['recommendations']:
            text_output += f"\n\n### Рекомендации:\n" + "\n".join([f"- {rec}" for rec in results['recommendations']])
        
        # Создаем график оценок
        try:
            import matplotlib.pyplot as plt
            import numpy as np
            
            if detailed:
                categories = list(detailed.keys())
                scores = list(detailed.values())
                
                # Преобразуем названия категорий на русский
                categories_ru = []
                for cat in categories:
                    ru_map = {
                        'floors': 'Полы',
                        'surfaces': 'Поверхности',
                        'furniture': 'Мебель',
                        'appliances': 'Техника',
                        'walls': 'Стены',
                        'windows': 'Окна',
                        'bathroom': 'Ванная',
                        'kitchen': 'Кухня'
                    }
                    categories_ru.append(ru_map.get(cat, cat))
                
                fig, ax = plt.subplots(figsize=(10, 6))
                bars = ax.barh(categories_ru, scores)
                
                # Раскрашиваем столбцы
                for bar, score in zip(bars, scores):
                    if score >= 80:
                        bar.set_color('green')
                    elif score >= 60:
                        bar.set_color('yellow')
                    else:
                        bar.set_color('red')
                
                ax.set_xlabel('Оценка (0-100)')
                ax.set_title('Детальная оценка уборки')
                ax.set_xlim(0, 100)
                
                # Добавляем значения на столбцы
                for bar in bars:
                    width = bar.get_width()
                    ax.text(width + 1, bar.get_y() + bar.get_height()/2,
                           f'{width:.0f}', ha='left', va='center')
                
                plt.tight_layout()
                chart_path = "assessment_chart.png"
                plt.savefig(chart_path)
                plt.close()
                
                return {
                    "text": text_output,
                    "chart": chart_path,
                    "before_image": before_img,
                    "after_image": after_img,
                    "overall_score": results.get('overall_score', 0),
                    "verdict": results.get('verdict', 'не определено')
                }
        except ImportError:
            print("Matplotlib не установлен, пропускаем создание графика")
        
        return {
            "text": text_output,
            "chart": None,
            "before_image": before_img,
            "after_image": after_img,
            "overall_score": results.get('overall_score', 0),
            "verdict": results.get('verdict', 'не определено')
        }


def create_gradio_interface():
    """
    Создание Gradio интерфейса
    """
    # Инициализируем модель при запуске
    model = CleaningAssessmentModel()
    
    def process_images(before_img, after_img):
        """
        Обработка изображений через Gradio
        """
        # Сохраняем временные файлы
        before_path = "temp_before_gradio.jpg"
        after_path = "temp_after_gradio.jpg"
        
        if before_img is not None:
            before_img.save(before_path)
        if after_img is not None:
            after_img.save(after_path)
        
        # Оцениваем уборку
        results = model.assess_cleaning(before_path, after_path)
        
        # Визуализируем результаты
        visualization = model.visualize_results(results, before_img, after_img)
        
        return (
            visualization['before_image'],
            visualization['after_image'],
            visualization['text'],
            visualization['chart'] if visualization['chart'] else None,
            visualization['overall_score'],
            visualization['verdict']
        )
    
    # Создаем интерфейс
    with gr.Blocks(title="Оценка качества уборки", theme=gr.themes.Soft()) as demo:
        gr.Markdown("# 🧹 Система оценки качества уборки")
        gr.Markdown("Загрузите изображения помещения до и после уборки для автоматической оценки")
        
        with gr.Row():
            with gr.Column():
                before_img = gr.Image(
                    label="Изображение ДО уборки",
                    type="pil",
                    height=300
                )
            
            with gr.Column():
                after_img = gr.Image(
                    label="Изображение ПОСЛЕ уборки",
                    type="pil",
                    height=300
                )
        
        submit_btn = gr.Button("Оценить уборку", variant="primary")
        
        with gr.Row():
            overall_score = gr.Number(
                label="Общая оценка",
                minimum=0,
                maximum=100
            )
            verdict = gr.Textbox(
                label="Вердикт",
                interactive=False
            )
        
        with gr.Row():
            output_text = gr.Markdown(label="Детальный отчет")
        
        with gr.Row():
            chart_output = gr.Image(
                label="Визуализация оценок",
                height=400
            )
        
        # Примеры для тестирования
        gr.Examples(
            examples=[
                ["example_before.jpg", "example_after.jpg"]
            ],
            inputs=[before_img, after_img],
            outputs=[output_text, chart_output, overall_score, verdict],
            fn=process_images,
            cache_examples=False
        )
        
        submit_btn.click(
            fn=process_images,
            inputs=[before_img, after_img],
            outputs=[before_img, after_img, output_text, chart_output, overall_score, verdict]
        )
    
    return demo


def main():
    """
    Основная функция
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Оценка качества уборки помещения")
    parser.add_argument("--mode", choices=["cli", "web"], default="web",
                       help="Режим работы: cli или web (по умолчанию: web)")
    parser.add_argument("--before", type=str, help="Путь к изображению до уборки (для CLI)")
    parser.add_argument("--after", type=str, help="Путь к изображению после уборки (для CLI)")
    
    args = parser.parse_args()
    
    if args.mode == "cli":
        if not args.before or not args.after:
            print("Для CLI режима укажите --before и --after аргументы")
            return
        
        # Проверяем существование файлов
        if not os.path.exists(args.before):
            print(f"Файл не найден: {args.before}")
            return
        
        if not os.path.exists(args.after):
            print(f"Файл не найден: {args.after}")
            return
        
        # Инициализируем модель и оцениваем
        model = CleaningAssessmentModel()
        results = model.assess_cleaning(args.before, args.after)
        
        # Выводим результаты
        print("\n" + "="*50)
        print("РЕЗУЛЬТАТЫ ОЦЕНКИ УБОРКИ")
        print("="*50)
        print(f"\nОбщая оценка: {results.get('overall_score', 0)}/100")
        print(f"Вердикт: {results.get('verdict', 'не определено')}")
        
        if 'detailed_scores' in results:
            print("\nДетальные оценки:")
            for category, score in results['detailed_scores'].items():
                print(f"  - {category}: {score}/100")
        
        if 'improvements' in results and results['improvements']:
            print("\nУлучшения:")
            for imp in results['improvements']:
                print(f"  ✓ {imp}")
        
        if 'issues' in results and results['issues']:
            print("\nПроблемы:")
            for issue in results['issues']:
                print(f"  ✗ {issue}")
        
        if 'recommendations' in results and results['recommendations']:
            print("\nРекомендации:")
            for rec in results['recommendations']:
                print(f"  • {rec}")
        
    else:
        # Запускаем веб-интерфейс
        demo = create_gradio_interface()
        demo.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False
        )


if __name__ == "__main__":
    # Установите необходимые зависимости:
    # pip install torch transformers gradio pillow matplotlib
    
    main()
