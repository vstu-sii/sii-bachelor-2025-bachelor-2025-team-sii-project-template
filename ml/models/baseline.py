import openai
from PIL import Image
import base64
from io import BytesIO

class CleaningAssessmentModel:
    def __init__(self, model_name="gpt-4-vision-preview"):
        self.model_name = model_name
        self.setup_api()
    
    def setup_api(self):
        # Настройка API ключей
        openai.api_key = os.getenv("OPENAI_API_KEY")
    
    def image_to_base64(self, image):
        """Конвертация изображения в base64"""
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        return base64.b64encode(buffered.getvalue()).decode()
    
    def assess_cleaning(self, image, prompt_template="detailed_assessment"):
        """Основная функция оценки"""
        try:
            base64_image = self.image_to_base64(image)
            
            response = openai.ChatCompletion.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": get_prompt(prompt_template)},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                            }
                        ]
                    }
                ],
                max_tokens=500
            )
            
            return self.parse_response(response.choices[0].message.content)
            
        except Exception as e:
            return {"error": str(e)}
    
    def parse_response(self, response_text):
        """Парсинг ответа модели"""
        # Регулярные выражения для извлечения структурированных данных
        import re
        # ... парсинг логика
        return parsed_data