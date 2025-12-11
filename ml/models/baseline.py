import json
import os
import time
from typing import Any, Dict, List, Optional, Tuple

from openai import OpenAI

from ml.prompt_templates import (
    PitchDeckPromptConfig,
    build_deck_generation_messages,
    build_slide_regeneration_messages,
)
from ml.tracing.langfuse_config import get_langfuse_client


_OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not _OPENAI_API_KEY:
    raise RuntimeError("Не установлен OPENAI_API_KEY в окружении")

_client = OpenAI(api_key=_OPENAI_API_KEY)
_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "gpt-4.1-mini")

_langfuse = get_langfuse_client()


def _extract_json(text: str) -> Dict[str, Any]:
    """Парсинг JSON из ответа модели (включая ```json ... ``` форматы)."""
    text = text.strip()
    if text.startswith("```"):
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            text = text[start : end + 1]
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Не удалось распарсить JSON из ответа LLM: {e}\n{text[:500]}")


def _chat_completion(
    messages: List[Dict[str, Any]],
    trace_name: str,
    max_retries: int = 3,
    base_delay: float = 1.0,
) -> Tuple[str, Dict[str, Optional[float]]]:
    """
    Один вызов LLM с retry и трассировкой в Langfuse.
    Возвращает: (content, stats) — контент и словарь с latency/tokens.
    """
    last_error: Optional[Exception] = None

    for attempt in range(1, max_retries + 1):
        trace = None
        if _langfuse is not None:
            try:
                trace = _langfuse.trace(
                    name=trace_name,
                    input={"messages": messages},
                    metadata={"model": _MODEL_NAME, "attempt": attempt},
                )
            except Exception:
                trace = None

        start = time.perf_counter()
        try:
            resp = _client.chat.completions.create(
                model=_MODEL_NAME,
                messages=messages,
                temperature=0.4,
            )
            latency_ms = (time.perf_counter() - start) * 1000.0

            content = resp.choices[0].message.content or ""
            usage = getattr(resp, "usage", None)

            stats = {
                "latency_ms": float(latency_ms),
                "prompt_tokens": float(getattr(usage, "prompt_tokens", 0) or 0),
                "completion_tokens": float(getattr(usage, "completion_tokens", 0) or 0),
                "total_tokens": float(getattr(usage, "total_tokens", 0) or 0),
            }

            if trace is not None:
                try:
                    trace.output = {"content": content, "usage": stats}
                    trace.end()
                except Exception:
                    pass

            return content, stats

        except Exception as e:  # сеть, лимиты и т.п.
            last_error = e
            if trace is not None:
                try:
                    trace.error = str(e)
                    trace.end()
                except Exception:
                    pass

            # если есть status_code и это явная клиентская ошибка — не ретраем
            status = getattr(e, "status_code", None)
            if status and status in (400, 401, 403, 404):
                break

            if attempt < max_retries:
                time.sleep(base_delay * (2 ** (attempt - 1)))
            else:
                break

    raise RuntimeError(f"Ошибка при вызове LLM после {max_retries} попыток: {last_error}")


def generate_deck(
    brief: str,
    config: PitchDeckPromptConfig,
) -> Dict[str, Any]:
    """
    Генерация полного дека.
    Возвращает dict: {"slides": [...]}.
    """
    deck, _ = generate_deck_with_stats(brief, config)
    return deck


def generate_deck_with_stats(
    brief: str,
    config: PitchDeckPromptConfig,
) -> Tuple[Dict[str, Any], Dict[str, Optional[float]]]:
    """
    То же, что generate_deck, но дополнительно возвращает stats:
    latency_ms, prompt_tokens, completion_tokens, total_tokens.
    Удобно для экспериментов в ноутбуке.
    """
    if not brief or not brief.strip():
        raise ValueError("brief не должен быть пустым")

    messages = build_deck_generation_messages(brief, config)
    raw, stats = _chat_completion(messages, trace_name="generate_deck")

    data = _extract_json(raw)
    slides = data.get("slides")
    if not isinstance(slides, list) or not slides:
        raise ValueError("Модель вернула некорректный формат: нет списка slides")

    norm_slides = []
    for i, s in enumerate(slides, start=1):
        norm_slides.append(
            {
                "id": int(s.get("id", i)),
                "section": (s.get("section") or "").strip(),
                "title": (s.get("title") or "").strip(),
                "bullets": [
                    b.strip()
                    for b in (s.get("bullets") or [])
                    if isinstance(b, str) and b.strip()
                ],
            }
        )

    return {"slides": norm_slides}, stats


def regenerate_slide(
    brief: str,
    existing_deck: Dict[str, Any],
    slide_id: int,
    config: PitchDeckPromptConfig,
) -> Dict[str, Any]:
    """
    Перегенерация одного слайда по id.
    Возвращает dict: {"id", "section", "title", "bullets"}.
    """
    if slide_id <= 0:
        raise ValueError("slide_id должен быть > 0")

    messages = build_slide_regeneration_messages(
        brief=brief,
        existing_deck=existing_deck,
        slide_id=slide_id,
        config=config,
    )
    raw, _stats = _chat_completion(messages, trace_name="regenerate_slide")
    slide = _extract_json(raw)

    required = ["id", "section", "title", "bullets"]
    if not all(k in slide for k in required):
        raise ValueError(f"Некорректный формат слайда, нет полей: {required}")

    return {
        "id": int(slide.get("id", slide_id)),
        "section": (slide.get("section") or "").strip(),
        "title": (slide.get("title") or "").strip(),
        "bullets": [
            b.strip()
            for b in (slide.get("bullets") or [])
            if isinstance(b, str) and b.strip()
        ],
    }
