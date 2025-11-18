# backend/app/routers/ai.py

from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class GenerateRequest(BaseModel):
    """
    Входная модель для генерации карточек.
    text — это учебный материал (упрощённо: обычный текст).
    """
    text: str


class Flashcard(BaseModel):
    """
    Одна карточка (вопрос-ответ).
    В MVP используем только question/answer.
    """
    question: str
    answer: str


class GenerateResponse(BaseModel):
    """
    Ответ сервиса генерации: список карточек.
    """
    cards: List[Flashcard]


@router.post("/generate", response_model=GenerateResponse)
async def generate_cards(payload: GenerateRequest) -> GenerateResponse:
    """
    Эндпоинт для генерации карточек на основе текста.
    MVP-реализация без реального LLM:
    - разбиваем текст на предложения;
    - делаем 3–5 простых карточек.
    """
    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Текст для генерации пустой")

    # Очень простая логика: разбиваем по точкам и берём первые несколько предложений
    sentences = [s.strip() for s in text.replace("?", ".").split(".") if s.strip()]

    cards: list[Flashcard] = []

    max_cards = 5
    for idx, sentence in enumerate(sentences[:max_cards], start=1):
        question = f"О чём говорится в предложении №{idx}?"
        answer = sentence
        cards.append(Flashcard(question=question, answer=answer))

    # Если текста мало, добавим одну fallback-карточку
    if not cards:
        cards.append(
            Flashcard(
                question="Какова основная идея этого текста?",
                answer=text,
            )
        )

    return GenerateResponse(cards=cards)
