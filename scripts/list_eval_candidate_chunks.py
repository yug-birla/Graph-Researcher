"""
List candidate chunks from processed documents for evaluation labeling.

Helps you fill relevant_chunk_ids in QA evaluation files by showing:
  - document ID
  - chunk ID
  - page metadata
  - chunk text preview

Usage:
  python scripts/list_eval_candidate_chunks.py --data-dir data/processed
  python scripts/list_eval_candidate_chunks.py --data-dir data/processed --document-id YOUR_ID --search "RAG"
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Optional


def load_chunks(processed_dir: str, document_id: str):
    """Load chunks from a processed document directory."""
    doc_dir = Path(processed_dir) / document_id
    chunks_file = doc_dir / "chunks.json"

    if not chunks_file.exists():
        return None

    with open(chunks_file, "r", encoding="utf-8") as f:
        return json.load(f)


def list_documents(processed_dir: str):
    """List all document IDs in the processed directory."""
    base = Path(processed_dir)
    if not base.exists():
        return []
    return [d.name for d in base.iterdir() if d.is_dir() and (d / "chunks.json").exists()]


def main():
    parser = argparse.ArgumentParser(description="List candidate chunks for eval labeling")
    parser.add_argument("--data-dir", default="data/processed", help="Processed data directory")
    parser.add_argument("--document-id", default=None, help="Specific document ID to inspect")
    parser.add_argument("--search", default=None, help="Filter chunks by text search term")
    parser.add_argument("--limit", type=int, default=50, help="Max chunks to show per document")
    parser.add_argument("--preview-length", type=int, default=200, help="Text preview character limit")
    args = parser.parse_args()

    docs = list_documents(args.data_dir)

    if not docs:
        print(f"No processed documents found in {args.data_dir}")
        sys.exit(0)

    if args.document_id:
        docs = [d for d in docs if d == args.document_id]
        if not docs:
            print(f"Document {args.document_id} not found. Available: {list_documents(args.data_dir)}")
            sys.exit(1)

    for doc_id in docs:
        chunks = load_chunks(args.data_dir, doc_id)
        if chunks is None:
            continue

        print(f"\n{'='*80}")
        print(f"Document: {doc_id}")
        print(f"Total chunks: {len(chunks)}")
        print(f"{'='*80}")

        shown = 0
        for chunk in chunks:
            if isinstance(chunk, dict):
                chunk_id = chunk.get("chunk_id", chunk.get("id", "unknown"))
                content = chunk.get("content", chunk.get("text", ""))
                page = chunk.get("page_number", "N/A")
                content_type = chunk.get("content_type", "text")
            else:
                chunk_id = getattr(chunk, "chunk_id", "unknown")
                content = getattr(chunk, "content", "")
                page = getattr(chunk, "page_number", "N/A")
                content_type = getattr(chunk, "content_type", "text")

            if args.search and args.search.lower() not in str(content).lower():
                continue

            preview = str(content)[:args.preview_length].replace("\n", " ").strip()
            print(f"\n  chunk_id:     {chunk_id}")
            print(f"  page:         {page}")
            print(f"  content_type: {content_type}")
            print(f"  preview:      {preview}")

            shown += 1
            if shown >= args.limit:
                remaining = len(chunks) - shown
                if remaining > 0:
                    print(f"\n  ... {remaining} more chunks. Use --limit to see more.")
                break


if __name__ == "__main__":
    main()
