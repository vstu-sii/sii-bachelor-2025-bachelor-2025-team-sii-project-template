import json
import os
import time
from typing import Any, Dict, List, Optional, Tuple

import requests

from ml.prompt_templates import (
    PitchDeckPromptConfig,
    build_deck_generation_messages,
    build_slide_regeneration_messages,
)
from ml.tracing.langfuse_config import get_langfuse_client


# ---------- конфиг провайдера LLM ----------

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")  # "openai" или "ollama"
_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "gpt-4.1-mini")

_openai_client = None
if LLM_PROVIDER == "openai":
    try:
        from openai import OpenAI  # type: ignore
    except Exception as e:
        raise RuntimeError(
            "Не удалось импортировать openai, а LLM_PROVIDER=openai. "
            "Установи пакет: pip install openai"
        ) from e

    _OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    if not _OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY не задан, а LLM_PROVIDER=openai")

    _openai_client = OpenAI(api_key=_OPENAI_API_KEY)

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

_langfuse = get_langfuse_client()


# ---------- вспомогательные функции ----------

def _extract_json(text: str) -> Dict[str, Any]:
    """
    Ищет JSON-объект в ответе модели (включая ```json ... ``` и текст вокруг).
    """
    raw = text.strip()

    if raw.startswith("```"):
        raw = raw.strip("`").strip()

    start = raw.find("{")
    end = raw.rfind("}")

    if start == -1 or end == -1 or start >= end:
        raise ValueError(
            "Ответ модели не содержит JSON-объект {...}. "
            f"Фрагмент ответа: {raw[:200]}"
        )

    json_str = raw[start : end + 1]

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Не удалось распарсить JSON из ответа LLM: {e}\n{json_str[:500]}"
        )


def _chat_completion(
    messages: List[Dict[str, Any]],
    trace_name: str,
    max_retries: int = 3,
    base_delay: float = 1.0,
) -> Tuple[str, Dict[str, Optional[float]]]:
    """
    Один вызов LLM с retry и трассировкой в Langfuse.
    Поддерживает провайдеров: openai, ollama.
    """
    last_error: Optional[Exception] = None

    for attempt in range(1, max_retries + 1):
        trace = None
        if _langfuse is not None:
            try:
                trace = _langfuse.trace(
                    name=trace_name,
                    input={"messages": messages},
                    metadata={
                        "model": _MODEL_NAME,
                        "provider": LLM_PROVIDER,
                        "attempt": attempt,
                    },
                )
            except Exception:
                trace = None

        start = time.perf_counter()

        try:
            # ---- OpenAI ----
            if LLM_PROVIDER == "openai":
                if _openai_client is None:
                    raise RuntimeError("OpenAI-клиент не инициализирован")

                resp = _openai_client.chat.completions.create(
                    model=_MODEL_NAME,
                    messages=messages,
                    temperature=0.4,
                )
                latency_ms = (time.perf_counter() - start) * 1000.0
                content = resp.choices[0].message.content or ""

                usage = getattr(resp, "usage", None)
                stats: Dict[str, Optional[float]] = {
                    "latency_ms": float(latency_ms),
                    "prompt_tokens": float(getattr(usage, "prompt_tokens", 0) or 0),
                    "completion_tokens": float(
                        getattr(usage, "completion_tokens", 0) or 0
                    ),
                    "total_tokens": float(getattr(usage, "total_tokens", 0) or 0),
                }

            # ---- Ollama ----
            elif LLM_PROVIDER == "ollama":
                ollama_messages = [
                    {"role": m["role"], "content": m["content"]} for m in messages
                ]
                r = requests.post(
                    f"{OLLAMA_HOST}/api/chat",
                    json={
                        "model": _MODEL_NAME,
                        "messages": ollama_messages,
                        "stream": False,
                    },
                    timeout=600,
                )
                r.raise_for_status()
                data = r.json()
                latency_ms = (time.perf_counter() - start) * 1000.0
                content = data["message"]["content"]

                stats = {
                    "latency_ms": float(latency_ms),
                    "prompt_tokens": None,
                    "completion_tokens": None,
                    "total_tokens": None,
                }

            else:
                raise RuntimeError(f"Неизвестный LLM_PROVIDER: {LLM_PROVIDER}")

            if trace is not None:
                try:
                    trace.output = {"content": content, "usage": stats}
                    trace.end()
                except Exception:
                    pass

            return content, stats

        except Exception as e:
            last_error = e
            if trace is not None:
                try:
                    trace.error = str(e)
                    trace.end()
                except Exception:
                    pass

            if attempt < max_retries:
                time.sleep(base_delay * (2 ** (attempt - 1)))
            else:
                break

    raise RuntimeError(
        f"Ошибка при вызове LLM после {max_retries} попыток: {last_error}"
    )


# ---------- публичные функции модели ----------

def generate_deck(
    brief: str,
    config: PitchDeckPromptConfig,
) -> Dict[str, Any]:
    deck, _ = generate_deck_with_stats(brief, config)
    return deck


def generate_deck_with_stats(
    brief: str,
    config: PitchDeckPromptConfig,
) -> Tuple[Dict[str, Any], Dict[str, Optional[float]]]:
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
