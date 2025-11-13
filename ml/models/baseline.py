import os
import re
import json
import time
import sys
import asyncio
import httpx
import requests
from dotenv import load_dotenv
from langfuse import Langfuse, observe  
from transformers import AutoTokenizer  

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from ml.prompt_templates import ( 
    UC_MATCHING_PROMPT, 
    UC_MATCHING_PROMPT_WITH_BENCHMARK,
    UC_QUESTION_GENERATION_PROMPT
)

# Загружаем переменные окружения
load_dotenv()

# Инициализируем Langfuse
langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
)

# Токенайзер для подсчета токенов
tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct-v0.2")

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
MISTRAL_URL = "https://api.mistral.ai/v1/chat/completions"
MISTRAL_MODEL = "mistral-small"

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")

MAX_RETRIES = 3
RETRY_DELAY = 2  # секунды

def _sanitize_json_string(s: str) -> str:
    """Удаляем управляющие символы, которые ломают JSON."""
    return re.sub(r'[\x00-\x1f\x7f]', ' ', s)

def count_tokens_and_cost(prompt: str, output: str, model: str = "mistral-small"):
    """Подсчет токенов и стоимости"""
    input_tokens = len(tokenizer.encode(prompt))
    output_tokens = len(tokenizer.encode(output))
    total_tokens = input_tokens + output_tokens

    # Тарифы для Mistral (примерные)
    price_per_input = 0.25 / 1_000_000
    price_per_output = 0.25 / 1_000_000
    cost = input_tokens * price_per_input + output_tokens * price_per_output

    return {
        "input": input_tokens,
        "output": output_tokens,
        "total": total_tokens,
    }, cost

class HRBaseline:
    """Бейслайн система для HR-оценки кандидатов"""
    
    def __init__(self):
        self.mistral = MistralHR()
    
    @observe()
    def evaluate_candidate_match(self, resume_analysis: dict, vacancy_data: dict, 
                           criteria_weights: dict = None, candidate_id: str = None) -> dict:
        """
        Оценка соответствия кандидата вакансии (только matching)
        """
        try:
            print("🎯 Оцениваем соответствие кандидата вакансии...")
            
            # Обновляем trace с информацией о задаче
            langfuse.update_current_generation(
                name="candidate_evaluation",
                input={
                    "resume_analysis": resume_analysis,
                    "vacancy_data": vacancy_data,
                    "criteria_weights": criteria_weights,
                    "candidate_id": candidate_id
                },
                metadata={"task_type": "candidate_evaluation"}
            )
            
            matching_result = self.mistral.match_vacancy_with_resume(
                resume_analysis=resume_analysis,
                vacancy_data=vacancy_data,
                criteria_weights=criteria_weights,
                candidate_id=candidate_id
            )
            
            if "error" in matching_result:
                langfuse.update_current_generation(
                    output={"error": matching_result["error"]},
                    level="ERROR"
                )
                return {"error": f"Matching failed: {matching_result['error']}"}
            
            overall_score = matching_result.get('matching_results', {}).get('overall_score', 0)
            print(f"✅ Оценка соответствия: {overall_score}/100")
            
            result = {
                "candidate_evaluation": matching_result,
                "summary": {
                    "overall_score": overall_score,
                    "suitability": matching_result.get('matching_results', {}).get('is_suitable', False),
                    "critical_issues_count": len(matching_result.get('matching_results', {}).get('critical_issues', [])),
                    "candidate_id": matching_result.get('candidate_info', {}).get('candidate_id', '')
                }
            }
            
            # Обновляем trace с результатом
            langfuse.update_current_generation(
                output=result,
                metadata={"overall_score": overall_score}
            )
            
            return result
            
        except Exception as e:
            langfuse.update_current_generation(
                output={"error": str(e)},
                level="ERROR"
            )
            return {"error": f"Candidate evaluation failed: {str(e)}"}

    @observe()
    def generate_interview_questions(self, resume_analysis: dict, vacancy_requirements: dict,
                                skill_gaps: list = None, strengths: list = None, 
                                experience_summary: str = None) -> dict:
        """
        Генерация вопросов для интервью (отдельная функция)
        """
        try:
            print("📝 Генерируем вопросы для интервью...")
            
            langfuse.update_current_generation(
                name="questions_generation",
                input={
                    "resume_analysis": resume_analysis,
                    "vacancy_requirements": vacancy_requirements,
                    "skill_gaps": skill_gaps,
                    "strengths": strengths,
                    "experience_summary": experience_summary
                },
                metadata={"task_type": "questions_generation"}
            )
            
            questions_result = asyncio.run(self.mistral.generate_interview_questions(
                resume_analysis=resume_analysis,
                vacancy_requirements=vacancy_requirements,
                skill_gaps=skill_gaps,
                strengths=strengths,
                experience_summary=experience_summary
            ))
            
            if "error" in questions_result:
                langfuse.update_current_generation(
                    output={"error": questions_result["error"]},
                    level="ERROR"
                )
                return {"error": f"Questions generation failed: {questions_result['error']}"}
            
            questions_count = len(questions_result.get('questions', []))
            result = {
                "interview_preparation": questions_result,
                "summary": {
                    "questions_count": questions_count,
                    "interview_duration": questions_result.get('interview_plan', {}).get('duration_minutes', '60'),
                    "question_types": list(set([q.get('type', '') for q in questions_result.get('questions', [])]))
                }
            }
            
            langfuse.update_current_generation(
                output=result,
                metadata={"questions_count": questions_count}
            )
            
            return result
            
        except Exception as e:
            langfuse.update_current_generation(
                output={"error": str(e)},
                level="ERROR"
            )
            return {"error": f"Interview questions generation failed: {str(e)}"}
    
    @observe()
    def compare_with_benchmark(self, resume_analysis: dict, vacancy_data: dict, 
                             benchmark_analysis: dict, criteria_weights: dict = None) -> dict:
        """
        Сравнительный анализ с эталонной оценкой
        """
        try:
            print("📊 Проводим сравнительный анализ с эталоном...")
            
            langfuse.update_current_generation(
                name="benchmark_comparison",
                input={
                    "resume_analysis": resume_analysis,
                    "vacancy_data": vacancy_data,
                    "benchmark_analysis": benchmark_analysis,
                    "criteria_weights": criteria_weights
                },
                metadata={"task_type": "benchmark_comparison"}
            )
            
            comparison_result = asyncio.run(self.mistral.compare_with_benchmark(
                resume_analysis=resume_analysis,
                vacancy_data=vacancy_data,
                benchmark_analysis=benchmark_analysis,
                criteria_weights=criteria_weights
            ))
            
            langfuse.update_current_generation(output=comparison_result)
            return comparison_result
            
        except Exception as e:
            langfuse.update_current_generation(
                output={"error": str(e)},
                level="ERROR"
            )
            return {"error": f"Benchmark comparison failed: {str(e)}"}
        
class MistralHR:
    """Класс для работы с Mistral API для HR-задач"""
    
    def __init__(self):
        self.api_key = MISTRAL_API_KEY
        self.model = MISTRAL_MODEL
        self.url = MISTRAL_URL
    
    @observe(as_type="generation")
    def match_vacancy_with_resume(self, resume_analysis: dict, vacancy_data: dict, 
                                criteria_weights: dict = None, candidate_id: str = None) -> dict:
        """
        Сопоставляет требования вакансии с данными кандидата
        """
        # Веса по умолчанию 
        default_weights = {
            'job_title_weight': 0.2,
            'education_weight': 0.15, 
            'experience_weight': 0.25,
            'schedule_weight': 0.10,
            'format_weight': 0.10,
            'additional_weight': 0.20
        }
        
        weights = {**default_weights, **(criteria_weights or {})}
        
        # Генерируем candidate_id если не передан
        if candidate_id is None:
            candidate_id = f"candidate_{int(time.time())}"
        
        prompt_text = UC_MATCHING_PROMPT.format_messages(
            candidate_id=candidate_id,
            job_title=vacancy_data.get("job_title", ""),
            education=vacancy_data.get("education", ""),
            work_experience=vacancy_data.get("work_experience", 0),
            desired_salary=vacancy_data.get("desired_salary", 0),
            work_schedule=vacancy_data.get("work_schedule", ""),
            work_format=vacancy_data.get("work_format", ""),
            additional_requirements=vacancy_data.get("additional_requirements", ""),
            resume_analysis=str(resume_analysis),
            job_title_weight=weights['job_title_weight'],
            education_weight=weights['education_weight'],
            experience_weight=weights['experience_weight'],
            schedule_weight=weights['schedule_weight'],
            format_weight=weights['format_weight'],
            additional_weight=weights['additional_weight']
        )
        
        prompt_text = "\n".join([m.content for m in prompt_text])
        
        # Обновляем информацию о генерации
        langfuse.update_current_generation(
            name="candidate_matching",
            input={
                "resume_analysis": resume_analysis,
                "vacancy_data": vacancy_data,
                "criteria_weights": criteria_weights
            },
            model=self.model,
            metadata={"task_type": "candidate_matching"}
        )
        
        result = self._call_mistral_api(prompt_text)
        
        # Подсчет токенов и стоимости
        output_text = str(result)
        usage_details, cost = count_tokens_and_cost(prompt_text, output_text)
        
        langfuse.update_current_generation(
            output=result,
            usage_details=usage_details,
            cost_details={"total": cost},
            metadata={"candidate_id": candidate_id}
        )
        
        return result
    
    @observe(as_type="generation")
    async def generate_interview_questions(self, resume_analysis: dict, vacancy_requirements: dict,
                                    skill_gaps: list = None, strengths: list = None, 
                                    experience_summary: str = None) -> dict:
        """
        Генерация персонализированных вопросов для интервью
        """
        prompt_text = UC_QUESTION_GENERATION_PROMPT.format_messages(
            resume_analysis=str(resume_analysis),
            vacancy_requirements=str(vacancy_requirements),
            additional_instructions="Сгенерируй разнообразные вопросы, охватывающие все аспекты кандидата",
            skill_gaps=", ".join(skill_gaps) if skill_gaps else "не выявлены",
            strengths=", ".join(strengths) if strengths else "опыт работы",
            experience_summary=experience_summary or "требует уточнения"
        )
        
        prompt_text = "\n".join([m.content for m in prompt_text])
        
        # Обновляем информацию о генерации
        langfuse.update_current_generation(
            name="questions_generation",
            input={
                "resume_analysis": resume_analysis,
                "vacancy_requirements": vacancy_requirements,
                "skill_gaps": skill_gaps,
                "strengths": strengths
            },
            model=self.model,
            metadata={"task_type": "questions_generation"}
        )
        
        result = await self._call_mistral_api_async(prompt_text)
        
        # Подсчет токенов и стоимости
        output_text = str(result)
        usage_details, cost = count_tokens_and_cost(prompt_text, output_text)
        
        questions_count = len(result.get('questions', [])) if isinstance(result, dict) else 0
        
        langfuse.update_current_generation(
            output=result,
            usage_details=usage_details,
            cost_details={"total": cost},
            metadata={"questions_count": questions_count}
        )
        
        return result
    
    @observe(as_type="generation")
    async def compare_with_benchmark(self, resume_analysis: dict, vacancy_data: dict,
                                   benchmark_analysis: dict, criteria_weights: dict = None) -> dict:
        """
        Сравнительный анализ с эталонной оценкой
        """
        benchmark_score = benchmark_analysis.get('matching_results', {}).get('overall_score', 0)
        
        prompt_text = UC_MATCHING_PROMPT_WITH_BENCHMARK.format_messages(
            benchmark_analysis=str(benchmark_analysis),
            resume_analysis=str(resume_analysis),
            benchmark_score=benchmark_score,
            job_title=vacancy_data.get("job_title", ""),
            education=vacancy_data.get("education", ""),
            work_experience=vacancy_data.get("work_experience", 0),
            work_schedule=vacancy_data.get("work_schedule", ""),
            work_format=vacancy_data.get("work_format", ""),
            additional_requirements=vacancy_data.get("additional_requirements", "")
        )
        
        prompt_text = "\n".join([m.content for m in prompt_text])
        
        # Обновляем информацию о генерации
        langfuse.update_current_generation(
            name="benchmark_comparison",
            input={
                "resume_analysis": resume_analysis,
                "vacancy_data": vacancy_data,
                "benchmark_score": benchmark_score
            },
            model=self.model,
            metadata={"task_type": "benchmark_comparison"}
        )
        
        result = await self._call_mistral_api_async(prompt_text)
        
        # Подсчет токенов и стоимости
        output_text = str(result)
        usage_details, cost = count_tokens_and_cost(prompt_text, output_text)
        
        langfuse.update_current_generation(
            output=result,
            usage_details=usage_details,
            cost_details={"total": cost}
        )
        
        return result
    
    def _call_mistral_api(self, prompt_text: str) -> dict:
        """Синхронный вызов Mistral API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt_text}
            ],
            "temperature": 0.4,
            "response_format": {"type": "json_object"}
        }
        
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = requests.post(self.url, headers=headers, json=payload, timeout=60)
                
                if response.status_code == 200:
                    result = response.json()
                    content = result['choices'][0]['message']['content']
                    return self._parse_json_response(content)
                else:
                    if attempt == MAX_RETRIES:
                        return {"error": f"Mistral API error: {response.status_code}"}
                    time.sleep(RETRY_DELAY)
                    
            except Exception as e:
                if attempt == MAX_RETRIES:
                    return {"error": f"Mistral API call failed: {str(e)}"}
                time.sleep(RETRY_DELAY)
        
        return {"error": "Failed after retries"}
    
    async def _call_mistral_api_async(self, prompt_text: str) -> dict:
        """Асинхронный вызов Mistral API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt_text}
            ],
            "temperature": 0.4,
            "response_format": {"type": "json_object"}
        }
        
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.post(self.url, headers=headers, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    content = result['choices'][0]['message']['content']
                    return self._parse_json_response(content)
                else:
                    if attempt == MAX_RETRIES:
                        return {"error": f"Mistral API error: {response.status_code}"}
                    await asyncio.sleep(RETRY_DELAY)
                    
            except Exception as e:
                if attempt == MAX_RETRIES:
                    return {"error": f"Mistral API call failed: {str(e)}"}
                await asyncio.sleep(RETRY_DELAY)
        
        return {"error": "Failed after retries"}
    
    def _parse_json_response(self, text: str) -> dict:
        """Парсинг JSON ответа от модели"""
        try:
            # Чистим Markdown
            clean = re.sub(r"^```(?:json)?", "", text.strip(), flags=re.IGNORECASE | re.MULTILINE)
            clean = re.sub(r"```$", "", clean.strip(), flags=re.MULTILINE)
            
            json_start = clean.find('{')
            json_end = clean.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                clean = clean[json_start:json_end]
            
            clean = _sanitize_json_string(clean)
            return json.loads(clean)
            
        except Exception as e:
            return {"error": f"JSON parsing failed: {str(e)}", "raw_output": text}
