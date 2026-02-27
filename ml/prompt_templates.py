from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class PitchDeckPromptConfig:
    """Настройки генерации питч-дека."""
    target_slide_count: int = 10
    tone: str = "formal"
    audience: str = "early-stage VC"
    language: str = "en"


SYSTEM_PROMPT_DECK_GENERATION = (
    "You are an AI assistant that generates investor pitch decks for startups. "
    "You always follow the instructions and output a valid JSON object with a list of slides. "
    "Each slide must have: 'id' (integer), 'section' (string), 'title' (string) and "
    "'bullets' (array of short sentences). Keep language concise and business-oriented."
)


def build_deck_generation_messages(
    brief: str,
    config: PitchDeckPromptConfig,
) -> List[Dict[str, Any]]:
    """
    Промпт для генерации всего дека.
    Требует обязательный слайд Market & Financials
    с описанием графиков/диаграмм.
    """
    user_content = f"""
Generate an investor pitch deck for the following startup.

[STARTUP_BRIEF]
{brief.strip()}
[/STARTUP_BRIEF]

Requirements:
- Number of slides: {config.target_slide_count}
- Tone: {config.tone}
- Audience: {config.audience}
- Language: {config.language}
- Mandatory sections: Problem, Solution, Market & Financials, Business Model, Traction (if available), Team, Roadmap (optional), Ask.
- You MUST include exactly one slide with section "Market & Financials".

Rules for the "Market & Financials" slide:
- The slide must contain:
  - Short description of the target market and key segments.
  - Basic financial information (revenue model and example numbers or ranges if they are given in the brief).
- You MUST add at least 1–2 bullets that explicitly describe charts or diagrams that could be shown on the slide.
  Examples of such bullets:
  - "Chart: bar chart showing TAM, SAM, SOM by segment."
  - "Chart: line chart of projected revenue by year."
  - "Diagram: pie chart of revenue split by product line."
- Do NOT invent very specific numbers if they are not in the brief; use generic phrasing (e.g. "growing market", "projected revenue growth over 3 years").

Output format (JSON):
{{
  "slides": [
    {{
      "id": 1,
      "section": "Problem",
      "title": "...",
      "bullets": ["...", "..."]
    }},
    {{
      "id": 2,
      "section": "Market & Financials",
      "title": "...",
      "bullets": ["...", "Chart: ...", "Diagram: ..."]
    }}
  ]
}}

General rules:
- Do NOT invent specific investor names or confidential partners.
- If the brief does not include numeric details, use only generic, non-precise wording for financials.
- Bullets must be short and scannable.
"""

    return [
        {"role": "system", "content": SYSTEM_PROMPT_DECK_GENERATION},
        {"role": "user", "content": user_content},
    ]


def build_slide_regeneration_messages(
    brief: str,
    existing_deck: Dict[str, Any],
    slide_id: int,
    config: PitchDeckPromptConfig,
) -> List[Dict[str, Any]]:
    """
    Промпт для перегенерации одного слайда.
    """
    user_content = f"""
You are improving a single slide inside an existing investor pitch deck.

[STARTUP_BRIEF]
{brief.strip()}
[/STARTUP_BRIEF]

[EXISTING_DECK_JSON]
{existing_deck}
[/EXISTING_DECK_JSON]

Task:
- Regenerate slide with id = {slide_id}.
- Keep the same high-level structure and section meaning.
- Improve clarity and conciseness of the title and bullets.
- Maintain tone: {config.tone}
- Audience: {config.audience}

Output format (JSON):
{{
  "id": {slide_id},
  "section": "...",
  "title": "...",
  "bullets": ["...", "..."]
}}
"""

    return [
        {"role": "system", "content": SYSTEM_PROMPT_DECK_GENERATION},
        {"role": "user", "content": user_content},
    ]
