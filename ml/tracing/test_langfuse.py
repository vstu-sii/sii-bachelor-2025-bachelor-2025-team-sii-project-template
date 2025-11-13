import json
import time

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from ml.models.baseline import HRBaseline, langfuse

# Пример использования
if __name__ == "__main__":
    hr_system = HRBaseline()
    
    # Пример данных
    resume_data = {
        "name": "Иван Иванов",
        "position": "Python разработчик",
        "experience": "3 года",
        "skills": ["Python", "Django", "SQL"],
        "education": "Высшее техническое"
    }
    
    vacancy_data = {
        "job_title": "Python Developer",
        "education": "Высшее техническое",
        "work_experience": "2",
        "desired_salary": "150000",
        "work_schedule": "полный день",
        "work_format": "офис",
        "additional_requirements": "Знание Python, Django, SQL"
    }
    
    print("🚀 Testing HR system with Langfuse tracing...")
    
    # Полная оценка кандидата
    matching = hr_system.evaluate_candidate_match(
        resume_analysis=resume_data,
        vacancy_data=vacancy_data,
        candidate_id="ivan_ivanov_cv.pdf"
    )
    
    questions = hr_system.generate_interview_questions(
        resume_analysis=resume_data,
        vacancy_requirements=vacancy_data
    )
    print(json.dumps(matching, ensure_ascii=False, indent=2))
    print(json.dumps(questions, ensure_ascii=False, indent=2))
    print("✅ Results received!")
    
    # Принудительно отправляем данные
    langfuse.flush()
    time.sleep(5)
    
    print("🎉 Check https://cloud.langfuse.com for detailed traces!")
    print("🔍 Look for: candidate_evaluation, questions_generation, candidate_matching")