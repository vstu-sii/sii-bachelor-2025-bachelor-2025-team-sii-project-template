from ml.models.baseline import generate_deck_with_stats
from ml.prompt_templates import PitchDeckPromptConfig

def main() -> None:
    brief = (
        "AI Pitch Deck Generator is a SaaS tool that helps startup founders "
        "generate investor-ready pitch decks from short textual briefs."
    )

    config = PitchDeckPromptConfig(
        target_slide_count=10,
        tone="formal",
        audience="early-stage VC",
        language="en",
    )

    deck, stats = generate_deck_with_stats(brief, config)

    print("=== Stats ===")
    print(stats)
    print()
    print("=== First slide ===")
    first = deck["slides"][0]
    print(first["id"], first["section"], "-", first["title"])
    for b in first["bullets"]:
        print(" •", b)

if __name__ == "__main__":
    main()
