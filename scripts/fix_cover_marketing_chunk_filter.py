from pathlib import Path

path = Path("app/graph/graph_quality.py")
text = path.read_text(encoding="utf-8-sig")
text = text.replace("\ufeff", "")

extra = r'''


def is_cover_or_marketing_chunk_text(text: str) -> bool:
    """
    Filters cover pages, marketing pages, career-pitch pages,
    and table-like project overview pages.

    These chunks often contain the query keyword but are weak evidence.
    """

    lower = str(text or "").lower()

    bad_phrases = [
        "master guide",
        "what you will build",
        "why it matters for your career",
        "from absolute beginner",
        "senior ai / ml / mlops engineer",
        "production-grade rag system",
        "no vector databases",
        "no gpu",
        "no paid apis",
        "demonstrates mastery",
        "proves you can ship",
        "shows you understand",
        "career",
        "portfolio-ready",
        "resume-worthy"
    ]

    hit_count = sum(1 for phrase in bad_phrases if phrase in lower)

    return hit_count >= 2
'''

if "def is_cover_or_marketing_chunk_text" not in text:
    text += extra

path.write_text(text, encoding="utf-8")
print("Added cover/marketing chunk filter.")
