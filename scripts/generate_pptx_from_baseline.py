from __future__ import annotations

import os
import re
from typing import Dict, Any, List, Optional

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE
from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE
from pptx.dml.color import RGBColor

from ml.models.baseline import generate_deck
from ml.prompt_templates import PitchDeckPromptConfig


BRIEF = (
    "AI Pitch Deck Generator is a SaaS tool that helps startup founders "
    "generate investor-ready pitch decks from short textual briefs."
)

SECTION_IMAGE_FILES = {
    "problem": "assets/problem.jpg",
    "solution": "assets/solution.jpg",
    "market": "assets/market.jpg",
    "financial": "assets/financial.jpg",
    "business model": "assets/solution.jpg",
    "traction": "assets/market.jpg",
    "team": "assets/team.jpg",
    "ask": "assets/ask.jpg",
}


def get_local_image_for_section(section: str) -> Optional[str]:
    s = section.lower()
    for key, path in SECTION_IMAGE_FILES.items():
        if key in s and os.path.exists(path):
            return path
    default_path = "assets/default.jpg"
    if os.path.exists(default_path):
        return default_path
    return None


def extract_numbers(text: str) -> List[float]:
    nums = re.findall(r"\d+\.?\d*", text)
    return [float(n) for n in nums]


def add_market_chart(slide, bullets: List[str]) -> None:
    joined = " ".join(bullets)
    numbers = extract_numbers(joined)

    if len(numbers) >= 3:
        categories = [f"Metric {i+1}" for i in range(len(numbers))]
        values = numbers
    else:
        categories = ["TAM", "SAM", "SOM"]
        values = (100, 60, 30)

    chart_data = CategoryChartData()
    chart_data.categories = categories
    chart_data.add_series("Market/Financials", values)

    x = Inches(7.0)
    y = Inches(2.0)
    cx = Inches(3.3)
    cy = Inches(3.0)

    chart_frame = slide.shapes.add_chart(
        XL_CHART_TYPE.COLUMN_CLUSTERED, x, y, cx, cy, chart_data
    )
    chart = chart_frame.chart

    chart.has_legend = False
    chart.value_axis.has_title = False
    chart.category_axis.has_title = False


def build_presentation(deck: Dict[str, Any], filename: str = "pitch_deck_generated.pptx") -> None:
    prs = Presentation()

    # титульный
    title_layout = prs.slide_layouts[0]
    slide0 = prs.slides.add_slide(title_layout)
    slide0.shapes.title.text = "AI Pitch Deck Generator"
    slide0.placeholders[1].text = "Auto-generated investor deck (baseline model)"

    # контентные
    bullet_layout = prs.slide_layouts[1]

    for s in deck["slides"]:
        section = s.get("section", "")
        title = s.get("title", "")
        bullets = s.get("bullets") or []

        slide = prs.slides.add_slide(bullet_layout)

        # заголовок
        title_shape = slide.shapes.title
        title_shape.text = f"{section}: {title}"
        title_tf = title_shape.text_frame
        if title_tf.paragraphs:
            title_tf.paragraphs[0].font.size = Pt(30)

        # текст слева
        body = slide.placeholders[1]
        body.left = Inches(0.7)
        body.top = Inches(2.0)
        body.width = Inches(5.8)
        body.height = Inches(4.0)

        tf = body.text_frame
        tf.clear()

        for i, bullet in enumerate(bullets):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.text = bullet
            p.level = 0
            p.font.size = Pt(18)

        # правый блок
        img_left = Inches(7.0)
        img_top = Inches(2.0)
        img_width = Inches(3.3)
        img_height = Inches(3.0)

        if "market" in section.lower() and "financial" in section.lower():
            add_market_chart(slide, bullets)
        else:
            img_path = get_local_image_for_section(section)
            if img_path:
                slide.shapes.add_picture(img_path, img_left, img_top, width=img_width)
            else:
                shape = slide.shapes.add_shape(
                    MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE,
                    img_left,
                    img_top,
                    img_width,
                    img_height,
                )
                shape.text = "Image placeholder"
                fill = shape.fill
                fill.solid()
                fill.fore_color.rgb = RGBColor(0xF0, 0xF0, 0xF0)
                shape.line.width = Pt(1)
                shape.text_frame.paragraphs[0].font.size = Pt(12)

    prs.save(filename)
    print(f"Presentation saved to: {filename}")


def main() -> None:
    config = PitchDeckPromptConfig(
        target_slide_count=10,
        tone="formal",
        audience="early-stage VC",
        language="en",
    )
    deck = generate_deck(BRIEF, config)
    build_presentation(deck, "pitch_deck_generated.pptx")


if __name__ == "__main__":
    main()
