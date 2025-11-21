# backend/app/routers/decks.py

from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

# Временное хранилище в памяти (MVP без реальной БД)
DECKS_DB: dict[int, dict] = {}
NEXT_DECK_ID = 1


class DeckCreate(BaseModel):
    """
    Модель для создания новой колоды (Pydantic-схема для API).
    """
    title: str
    description: str | None = None


class Deck(DeckCreate):
    """
    Модель колоды с идентификатором (ответ API).
    """
    id: int


@router.get("/", response_model=List[Deck])
async def list_decks() -> List[Deck]:
    """
    Получить список всех колод (MVP-реализация, без фильтрации по пользователю).
    Данные хранятся в памяти процесса (DECKS_DB).
    """
    return [Deck(**deck) for deck in DECKS_DB.values()]


@router.post("/", response_model=Deck, status_code=201)
async def create_deck(payload: DeckCreate) -> Deck:
    """
    Создать новую колоду. В MVP сохраняем только в памяти.

    В дальнейшем здесь можно будет:
    - сохранять колоду в реальную БД через ORM-модель (models.Deck);
    - привязывать колоду к пользователю (owner_id).
    """
    global NEXT_DECK_ID  # noqa: PLW0603

    deck_id = NEXT_DECK_ID
    NEXT_DECK_ID += 1

    deck_data = {
        "id": deck_id,
        "title": payload.title,
        "description": payload.description,
    }
    DECKS_DB[deck_id] = deck_data
    return Deck(**deck_data)


@router.get("/{deck_id}", response_model=Deck)
async def get_deck(deck_id: int) -> Deck:
    """
    Получить конкретную колоду по id.
    """
    deck = DECKS_DB.get(deck_id)
    if not deck:
        raise HTTPException(status_code=404, detail="Колода не найдена")
    return Deck(**deck)


@router.delete("/{deck_id}", status_code=204)
async def delete_deck(deck_id: int) -> None:
    """
    Удалить колоду по id.
    """
    if deck_id not in DECKS_DB:
        raise HTTPException(status_code=404, detail="Колода не найдена")
    DECKS_DB.pop(deck_id)
