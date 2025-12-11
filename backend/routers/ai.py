from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ml.models.baseline import generate_deck, regenerate_slide
from ml.prompt_templates import PitchDeckPromptConfig


router = APIRouter(prefix="/ai", tags=["ai"])


class Slide(BaseModel):
    id: int = Field(..., description="Порядковый номер слайда")
    section: str = Field(..., description="Тип секции (Problem, Solution, Market и т.п.)")
    title: str = Field(..., description="Заголовок слайда")
    bullets: List[str] = Field(..., description="Краткие тезисы")


class GenerateDeckRequest(BaseModel):
    brief: str = Field(..., min_length=20, description="Описание стартапа на английском")
    target_slide_count: int = Field(
        10, ge=4, le=20, description="Желаемое количество слайдов"
    )
    tone: str = Field("formal", description="Тон: formal / storytelling / technical")
    audience: str = Field("early-stage VC", description="Целевая аудитория")
    language: str = Field("en", description="Язык презентации (baseline: en)")


class GenerateDeckResponse(BaseModel):
    slides: List[Slide]


class RegenerateSlideRequest(BaseModel):
    brief: str = Field(..., min_length=20, description="Описание стартапа на английском")
    existing_deck: Dict[str, Any] = Field(
        ..., description='JSON дека в формате {"slides": [...]}'
    )
    slide_id: int = Field(..., ge=1, description="ID слайда для перегенерации")
    tone: str = Field("formal", description="Тон")
    audience: str = Field("early-stage VC", description="Целевая аудитория")
    language: str = Field("en", description="Язык")


class RegenerateSlideResponse(Slide):
    pass


@router.get("/health", summary="Проверка работоспособности AI-модуля")
async def health() -> Dict[str, str]:
    return {"status": "ok"}


@router.post(
    "/generate-deck",
    response_model=GenerateDeckResponse,
    summary="Сгенерировать питч-дек",
    description="Генерирует набор слайдов по описанию стартапа.",
)
async def generate_deck_endpoint(req: GenerateDeckRequest) -> Dict[str, Any]:
    config = PitchDeckPromptConfig(
        target_slide_count=req.target_slide_count,
        tone=req.tone,
        audience=req.audience,
        language=req.language,
    )
    try:
        deck = generate_deck(brief=req.brief, config=config)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return deck


@router.post(
    "/regenerate-slide",
    response_model=RegenerateSlideResponse,
    summary="Перегенерировать один слайд",
    description="Улучшает конкретный слайд в рамках существующего дека.",
)
async def regenerate_slide_endpoint(req: RegenerateSlideRequest) -> Dict[str, Any]:
    slides = req.existing_deck.get("slides")
    if not isinstance(slides, list) or not slides:
        raise HTTPException(status_code=400, detail="existing_deck.slides должен быть непустым списком")

    config = PitchDeckPromptConfig(
        target_slide_count=len(slides),
        tone=req.tone,
        audience=req.audience,
        language=req.language,
    )

    try:
        slide = regenerate_slide(
            brief=req.brief,
            existing_deck=req.existing_deck,
            slide_id=req.slide_id,
            config=config,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return slide
