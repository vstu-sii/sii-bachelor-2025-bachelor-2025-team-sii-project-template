from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ml.models.baseline import generate_deck, regenerate_slide
from ml.prompt_templates import PitchDeckPromptConfig


router = APIRouter(prefix="/ai", tags=["ai"])


class Slide(BaseModel):
    id: int
    section: str
    title: str
    bullets: List[str]


class Deck(BaseModel):
    slides: List[Slide]


class GenerateDeckRequest(BaseModel):
    brief: str = Field(..., description="Free-text startup description")
    target_slide_count: int = 10
    tone: str = "formal"
    audience: str = "early-stage VC"
    language: str = "en"


class GenerateDeckResponse(BaseModel):
    slides: List[Slide]


class RegenerateSlideRequest(BaseModel):
    brief: str
    existing_deck: Deck
    slide_id: int = Field(..., gt=0)
    tone: str = "formal"
    audience: str = "early-stage VC"
    language: str = "en"


class RegenerateSlideResponse(BaseModel):
    slide: Slide


@router.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@router.post("/generate-deck", response_model=GenerateDeckResponse)
async def generate_deck_endpoint(payload: GenerateDeckRequest) -> GenerateDeckResponse:
    config = PitchDeckPromptConfig(
        target_slide_count=payload.target_slide_count,
        tone=payload.tone,
        audience=payload.audience,
        language=payload.language,
    )

    deck_dict = generate_deck(payload.brief, config)
    slides = [Slide(**s) for s in deck_dict["slides"]]
    return GenerateDeckResponse(slides=slides)


@router.post("/regenerate-slide", response_model=RegenerateSlideResponse)
async def regenerate_slide_endpoint(
    payload: RegenerateSlideRequest,
) -> RegenerateSlideResponse:
    if not payload.existing_deck.slides:
        raise HTTPException(status_code=400, detail="existing_deck.slides is empty")

    config = PitchDeckPromptConfig(
        target_slide_count=len(payload.existing_deck.slides),
        tone=payload.tone,
        audience=payload.audience,
        language=payload.language,
    )

    deck_dict = payload.existing_deck.model_dump()
    new_slide_dict = regenerate_slide(
        brief=payload.brief,
        existing_deck=deck_dict,
        slide_id=payload.slide_id,
        config=config,
    )
    return RegenerateSlideResponse(slide=Slide(**new_slide_dict))
