# Lab3: AI Engineer — Prototype

## 1. Артефакты

- `ml/models/baseline.py`  
  Baseline LLM-модель:
  - выбор модели через `LLM_MODEL_NAME` (дефолт `gpt-4.1-mini`)
  - генерация дека: `generate_deck` / `generate_deck_with_stats`
  - перегенерация слайда: `regenerate_slide`
  - retry + парсинг JSON
  - трейсинг всех вызовов через Langfuse

- `ml/tracing/langfuse_config.py`  
  - инициализация клиента Langfuse
  - чтение ключей из env: `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_HOST`
  - fallback на dummy-клиент, если SDK/ключей нет (код не падает в dev-режиме)

- `notebooks/baseline_experiments.ipynb`  
  - 5 тестовых кейсов (разные стартапы)
  - вызов `generate_deck_with_stats`
  - базовые метрики: latency (LLM, wall-time), token usage
  - сводка по средним значениям и сырые результаты

- `backend/routers/ai.py`  
  FastAPI-роутер:
  - `GET /ai/health` — проверка модуля
  - `POST /ai/generate-deck` — генерация дека
  - `POST /ai/regenerate-slide` — перегенерация одного слайда  
  Валидация через Pydantic, описания полей для автодокументации в `/docs`.

---

## 2. Установка и запуск

### Зависимости

`requirements.txt`:

```text
fastapi
uvicorn
openai
langfuse
pydantic
jupyter
