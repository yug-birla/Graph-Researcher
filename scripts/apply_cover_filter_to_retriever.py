from pathlib import Path

path = Path("app/graph/graph_guided_retriever.py")
text = path.read_text(encoding="utf-8-sig")
text = text.replace("\ufeff", "")

text = text.replace(
'''from app.graph.graph_quality import (
    is_low_quality_chunk_text,
    is_meta_showcase_chunk_text
)''',
'''from app.graph.graph_quality import (
    is_low_quality_chunk_text,
    is_meta_showcase_chunk_text,
    is_cover_or_marketing_chunk_text
)'''
)

old = '''        if is_meta_showcase_chunk_text(text_preview):
            continue

        final_score = info["score"] + query_text_relevance(query, text_preview)
'''

new = '''        if is_meta_showcase_chunk_text(text_preview):
            continue

        if is_cover_or_marketing_chunk_text(text_preview):
            continue

        final_score = info["score"] + query_text_relevance(query, text_preview)
'''

if old in text:
    text = text.replace(old, new)
    print("Added cover/marketing filter inside graph-guided retriever.")
else:
    print("Filter location already changed or not found.")

path.write_text(text, encoding="utf-8")
