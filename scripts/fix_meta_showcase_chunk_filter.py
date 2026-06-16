from pathlib import Path

path = Path("app/graph/graph_quality.py")
text = path.read_text(encoding="utf-8-sig")
text = text.replace("\ufeff", "")

extra = r'''


def is_meta_showcase_chunk_text(text: str) -> bool:
    """
    Filters chunks that are about project promotion, resume bullets,
    LinkedIn drafts, portfolio text, or deployment brag text.

    These chunks may contain good keywords, but they are usually not
    good answer evidence for conceptual questions like "What is RAG?"
    """

    lower = str(text or "").lower()

    bad_phrases = [
        "linkedin post",
        "linkedin post draft",
        "copy and customise",
        "copy and customize",
        "i just shipped",
        "resume bullet",
        "portfolio",
        "general software engineering",
        "built vectorless rag platform",
        "most ambitious project",
        "deployment framework",
        "zero external dependencies"
    ]

    return any(phrase in lower for phrase in bad_phrases)
'''

if "def is_meta_showcase_chunk_text" not in text:
    text += extra

path.write_text(text, encoding="utf-8")
print("Added meta/showcase chunk filter.")
