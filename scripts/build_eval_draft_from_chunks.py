"""
Build draft evaluation questions from processed chunks.

Generates candidate Q/A pairs from actual chunk content. These are DRAFTS
and MUST be reviewed and corrected before being used as gold evaluation data.

Output is written to: eval/qa_50_draft_needs_review.jsonl

Usage:
  python scripts/build_eval_draft_from_chunks.py --data-dir data/processed
  python scripts/build_eval_draft_from_chunks.py --data-dir data/processed --document-id YOUR_ID
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List


def load_chunks(processed_dir: str, document_id: str) -> list:
    doc_dir = Path(processed_dir) / document_id
    chunks_file = doc_dir / "chunks.json"
    if not chunks_file.exists():
        return []
    with open(chunks_file, "r", encoding="utf-8") as f:
        return json.load(f)


def list_documents(processed_dir: str) -> list:
    base = Path(processed_dir)
    if not base.exists():
        return []
    return [d.name for d in base.iterdir() if d.is_dir() and (d / "chunks.json").exists()]


def extract_key_terms(text: str) -> List[str]:
    """Extract candidate key terms from chunk text."""
    words = re.findall(r'[A-Z][a-zA-Z]{2,}(?:\s+[A-Z][a-zA-Z]{2,}){0,3}', text)
    # Also get acronyms
    acronyms = re.findall(r'\b[A-Z]{2,6}\b', text)
    terms = list(set(words + acronyms))
    return [t for t in terms if len(t) > 2][:5]


def generate_question_from_chunk(chunk: dict, chunk_index: int) -> Dict[str, Any]:
    """Generate a draft question from a chunk."""
    content = chunk.get("content", chunk.get("text", ""))
    chunk_id = chunk.get("chunk_id", chunk.get("id", f"chunk_{chunk_index}"))
    page = chunk.get("page_number", None)

    # Try to form a question from the first sentence
    sentences = re.split(r'(?<=[.!?])\s+', content.strip())
    first_sentence = sentences[0] if sentences else content[:100]

    key_terms = extract_key_terms(content)
    if key_terms:
        main_term = key_terms[0]
        question = f"What does the document say about {main_term}?"
    else:
        question = f"What is discussed in the content on page {page or 'N/A'}?"

    return {
        "id": f"q{chunk_index + 1:03d}",
        "question": question,
        "gold_answer": f"DRAFT_NEEDS_REVIEW: {first_sentence[:200]}",
        "relevant_chunk_ids": [str(chunk_id)],
        "expected_terms": [t.lower() for t in key_terms[:4]],
        "difficulty": "medium",
        "_source_page": page,
        "_source_preview": content[:150],
    }


def main():
    parser = argparse.ArgumentParser(description="Build draft eval questions from chunks")
    parser.add_argument("--data-dir", default="data/processed")
    parser.add_argument("--document-id", default=None)
    parser.add_argument("--max-questions", type=int, default=50)
    parser.add_argument("--output", default="eval/qa_50_draft_needs_review.jsonl")
    args = parser.parse_args()

    docs = list_documents(args.data_dir)
    if args.document_id:
        docs = [d for d in docs if d == args.document_id]

    if not docs:
        print(f"No processed documents found in {args.data_dir}")
        sys.exit(0)

    all_chunks = []
    for doc_id in docs:
        chunks = load_chunks(args.data_dir, doc_id)
        for c in chunks:
            if isinstance(c, dict):
                c["_document_id"] = doc_id
            all_chunks.append(c)

    print(f"Found {len(all_chunks)} chunks across {len(docs)} documents")

    # Filter to substantive chunks
    good_chunks = []
    for c in all_chunks:
        content = c.get("content", c.get("text", ""))
        if len(str(content)) >= 100:
            good_chunks.append(c)

    # Sample evenly
    step = max(1, len(good_chunks) // args.max_questions)
    selected = good_chunks[::step][:args.max_questions]

    questions = []
    for i, chunk in enumerate(selected):
        q = generate_question_from_chunk(chunk, i)
        questions.append(q)

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        for q in questions:
            f.write(json.dumps(q, ensure_ascii=False) + "\n")

    print(f"Wrote {len(questions)} draft questions to {args.output}")
    print(f"\nIMPORTANT: These are DRAFTS. Review and correct before using as gold evaluation data.")


if __name__ == "__main__":
    main()
