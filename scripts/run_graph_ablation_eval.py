"""
GraphResearcher  RAG vs RAG+Graph ablation evaluation.

Runs every question from a QA JSONL file in two modes:
  1. RAG only   (use_graph=False, use_graph_retrieval=False)
  2. RAG+Graph  (use_graph=True,  use_graph_retrieval=True)

Computes: Recall@3, Recall@5, Recall@10, answer faithfulness (heuristic),
answer completeness, average latency, average answer word count, error count.

Usage:
  python scripts/run_graph_ablation_eval.py \
      --base-url http://127.0.0.1:8000 \
      --document-id YOUR_DOCUMENT_ID \
      --qa-file eval/qa_15_starter.jsonl
"""

import argparse
import csv
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Metric helpers
# ---------------------------------------------------------------------------

def recall_at_k(retrieved_chunk_ids: List[str], gold_chunk_ids: List[str], k: int) -> float:
    """Fraction of gold relevant chunk IDs found in the top-k retrieved chunks."""
    if not gold_chunk_ids:
        return 0.0
    top_k = [str(c) for c in retrieved_chunk_ids[:k]]
    gold = [str(c) for c in gold_chunk_ids]
    hits = sum(1 for g in gold if g in top_k)
    return hits / len(gold)


def answer_completeness(answer: str, expected_terms: List[str]) -> float:
    """Fraction of expected gold terms present in the answer text."""
    if not expected_terms:
        return 0.0
    answer_lower = answer.lower()
    hits = sum(1 for term in expected_terms if term.lower() in answer_lower)
    return hits / len(expected_terms)


def answer_faithfulness_heuristic(answer: str, source_texts: List[str]) -> float:
    """
    Automatic estimated faithfulness.
    Splits the answer into claim-sentences and checks what fraction have
    at least one supporting sentence in the retrieved source context.
    This is a bag-of-words overlap heuristic, NOT human judgment.
    """
    if not answer or not source_texts:
        return 0.0

    sentences = re.split(r'(?<=[.!?])\s+', answer.strip())
    sentences = [s for s in sentences if len(s.split()) >= 4]  # skip very short

    if not sentences:
        return 0.0

    joined_sources = " ".join(source_texts).lower()
    source_tokens = set(re.findall(r'[a-z0-9]+', joined_sources))

    supported = 0
    for sentence in sentences:
        sent_tokens = set(re.findall(r'[a-z0-9]+', sentence.lower()))
        # remove trivial words
        sent_tokens -= {"the", "a", "an", "is", "are", "was", "were", "of",
                        "to", "and", "in", "on", "for", "it", "this", "that"}
        if not sent_tokens:
            supported += 1  # vacuously true
            continue
        overlap = len(sent_tokens & source_tokens) / len(sent_tokens)
        if overlap >= 0.5:
            supported += 1

    return supported / len(sentences)


# ---------------------------------------------------------------------------
# QA file loading and validation
# ---------------------------------------------------------------------------

REQUIRED_FIELDS = {"id", "question", "gold_answer", "relevant_chunk_ids", "expected_terms", "difficulty"}


def load_qa_file(path: str) -> List[Dict[str, Any]]:
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            missing = REQUIRED_FIELDS - set(row.keys())
            if missing:
                print(f"ERROR: Line {line_no} missing fields: {missing}")
                sys.exit(1)
            rows.append(row)
    return rows


def has_todo_values(rows: List[Dict[str, Any]]) -> bool:
    for row in rows:
        if "TODO" in row.get("gold_answer", ""):
            return True
        for cid in row.get("relevant_chunk_ids", []):
            if "TODO" in str(cid):
                return True
    return False


# ---------------------------------------------------------------------------
# API caller
# ---------------------------------------------------------------------------

def call_ask(base_url: str, document_id: str, question: str,
             use_graph: bool, use_graph_retrieval: bool,
             graph_entity_limit: int = 12,
             graph_retrieval_top_k: int = 8,
             top_k: int = 10) -> Dict[str, Any]:
    """Call the /ask endpoint and return (response_dict, latency_ms)."""
    import requests

    payload = {
        "query": question,
        "document_id": document_id,
        "top_k": top_k,
        "retrieval_mode": "hybrid",
        "use_reranker": True,
        "use_llm": True,
        "use_graph": use_graph,
        "graph_entity_limit": graph_entity_limit,
        "use_graph_retrieval": use_graph_retrieval,
        "graph_retrieval_top_k": graph_retrieval_top_k,
    }

    start = time.perf_counter()
    resp = requests.post(f"{base_url.rstrip('/')}/ask", json=payload, timeout=120)
    latency_ms = (time.perf_counter() - start) * 1000

    resp.raise_for_status()
    return resp.json(), latency_ms


def extract_retrieved_chunk_ids(response: Dict[str, Any]) -> List[str]:
    """Extract ordered list of chunk IDs from /ask response."""
    chunk_ids = []
    for src in response.get("sources", []):
        cid = src.get("chunk_id") or src.get("id") or ""
        if cid:
            chunk_ids.append(str(cid))
    return chunk_ids


def extract_source_texts(response: Dict[str, Any]) -> List[str]:
    """Extract source content texts for faithfulness check."""
    texts = []
    for src in response.get("sources", []):
        text = src.get("content") or src.get("text") or ""
        if text:
            texts.append(str(text))
    return texts


# ---------------------------------------------------------------------------
# Main eval loop
# ---------------------------------------------------------------------------

def run_mode(base_url: str, document_id: str, rows: List[Dict], *,
             use_graph: bool, use_graph_retrieval: bool,
             graph_entity_limit: int, graph_retrieval_top_k: int,
             mode_label: str) -> List[Dict]:
    """Run all questions in one mode, return per-row metrics."""
    results = []
    for i, row in enumerate(rows, 1):
        qid = row["id"]
        print(f"  [{mode_label}] {i}/{len(rows)} {qid}: {row['question'][:60]}...", end=" ", flush=True)
        try:
            resp, latency = call_ask(
                base_url, document_id, row["question"],
                use_graph=use_graph,
                use_graph_retrieval=use_graph_retrieval,
                graph_entity_limit=graph_entity_limit,
                graph_retrieval_top_k=graph_retrieval_top_k,
            )
            answer = resp.get("answer", "")
            retrieved = extract_retrieved_chunk_ids(resp)
            source_texts = extract_source_texts(resp)
            gold_ids = row.get("relevant_chunk_ids", [])
            expected = row.get("expected_terms", [])

            r3 = recall_at_k(retrieved, gold_ids, 3)
            r5 = recall_at_k(retrieved, gold_ids, 5)
            r10 = recall_at_k(retrieved, gold_ids, 10)
            faith = answer_faithfulness_heuristic(answer, source_texts)
            comp = answer_completeness(answer, expected)
            word_count = len(answer.split())

            results.append({
                "id": qid,
                "mode": mode_label,
                "question": row["question"],
                "difficulty": row["difficulty"],
                "recall_at_3": r3,
                "recall_at_5": r5,
                "recall_at_10": r10,
                "faithfulness": faith,
                "completeness": comp,
                "latency_ms": round(latency, 1),
                "answer_words": word_count,
                "error": "",
                "answer_preview": answer[:200],
            })
            print(f"OK  R@5={r5:.2f} faith={faith:.2f} comp={comp:.2f} {latency:.0f}ms")

        except Exception as exc:
            results.append({
                "id": qid,
                "mode": mode_label,
                "question": row["question"],
                "difficulty": row["difficulty"],
                "recall_at_3": 0.0,
                "recall_at_5": 0.0,
                "recall_at_10": 0.0,
                "faithfulness": 0.0,
                "completeness": 0.0,
                "latency_ms": 0.0,
                "answer_words": 0,
                "error": str(exc)[:200],
                "answer_preview": "",
            })
            print(f"ERR: {exc}")

    return results


def aggregate(results: List[Dict]) -> Dict[str, Any]:
    """Compute mean of per-row metrics."""
    if not results:
        return {}
    n = len(results)
    return {
        "n": n,
        "recall_at_3": round(sum(r["recall_at_3"] for r in results) / n, 4),
        "recall_at_5": round(sum(r["recall_at_5"] for r in results) / n, 4),
        "recall_at_10": round(sum(r["recall_at_10"] for r in results) / n, 4),
        "faithfulness": round(sum(r["faithfulness"] for r in results) / n, 4),
        "completeness": round(sum(r["completeness"] for r in results) / n, 4),
        "avg_latency_ms": round(sum(r["latency_ms"] for r in results) / n, 1),
        "avg_answer_words": round(sum(r["answer_words"] for r in results) / n, 1),
        "errors": sum(1 for r in results if r["error"]),
    }


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def write_reports(rag_results, graph_results, rag_agg, graph_agg, output_dir: str, qa_file: str):
    os.makedirs(output_dir, exist_ok=True)

    # --- CSV ---
    csv_path = os.path.join(output_dir, "eval_rows.csv")
    all_rows = rag_results + graph_results
    fieldnames = list(all_rows[0].keys()) if all_rows else []
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)

    # --- JSON summary ---
    summary = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "qa_file": qa_file,
        "modes": {
            "RAG": rag_agg,
            "RAG + Graph": graph_agg,
        },
        "ablation_conclusion": build_conclusion(rag_agg, graph_agg),
    }
    json_path = os.path.join(output_dir, "eval_summary.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    # --- Markdown report ---
    md_path = os.path.join(output_dir, "eval_report.md")
    conclusion = summary["ablation_conclusion"]
    md = f"""# GraphResearcher Evaluation Report

Generated: {summary['timestamp']}
QA file: `{qa_file}`

## Methodology

- **Recall@K**: fraction of manually labeled gold relevant chunk IDs retrieved in top K results.
- **Faithfulness**: automatic estimated faithfulness — heuristic check of whether generated answer claims are supported by retrieved source context. This is **not** human judgment.
- **Completeness**: fraction of expected gold terms present in the answer.
- **Latency**: end-to-end request time in milliseconds.

## Results

| Mode | Recall@3 | Recall@5 | Recall@10 | Faithfulness | Completeness | Avg Latency (ms) | Avg Answer Words | Errors |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| RAG | {rag_agg.get('recall_at_3', 'N/A')} | {rag_agg.get('recall_at_5', 'N/A')} | {rag_agg.get('recall_at_10', 'N/A')} | {rag_agg.get('faithfulness', 'N/A')} | {rag_agg.get('completeness', 'N/A')} | {rag_agg.get('avg_latency_ms', 'N/A')} | {rag_agg.get('avg_answer_words', 'N/A')} | {rag_agg.get('errors', 'N/A')} |
| RAG + Graph | {graph_agg.get('recall_at_3', 'N/A')} | {graph_agg.get('recall_at_5', 'N/A')} | {graph_agg.get('recall_at_10', 'N/A')} | {graph_agg.get('faithfulness', 'N/A')} | {graph_agg.get('completeness', 'N/A')} | {graph_agg.get('avg_latency_ms', 'N/A')} | {graph_agg.get('avg_answer_words', 'N/A')} | {graph_agg.get('errors', 'N/A')} |

## Ablation Conclusion

{conclusion}

## Notes

- Faithfulness is an automatic heuristic estimate. It checks whether answer sentences overlap with retrieved source tokens. It is **not** equivalent to human evaluation.
- If relevant_chunk_ids were TODO placeholders, Recall@K will be 0 because no gold IDs could be matched.
- Run with verified gold labels for meaningful Recall results.
"""
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md)

    print(f"\nReports written to {output_dir}/")
    print(f"  {csv_path}")
    print(f"  {json_path}")
    print(f"  {md_path}")


def build_conclusion(rag: Dict, graph: Dict) -> str:
    lines = []

    if not rag or not graph:
        return "Evaluation data insufficient to draw conclusions."

    # Recall
    r5_diff = graph.get("recall_at_5", 0) - rag.get("recall_at_5", 0)
    if r5_diff > 0.02:
        lines.append(f"- GraphRAG **improved** Recall@5 by {r5_diff:.4f}.")
    elif r5_diff < -0.02:
        lines.append(f"- GraphRAG **decreased** Recall@5 by {abs(r5_diff):.4f}.")
    else:
        lines.append("- GraphRAG had **no significant effect** on Recall@5.")

    # Faithfulness
    f_diff = graph.get("faithfulness", 0) - rag.get("faithfulness", 0)
    if f_diff > 0.02:
        lines.append(f"- GraphRAG **improved** estimated faithfulness by {f_diff:.4f}.")
    elif f_diff < -0.02:
        lines.append(f"- GraphRAG **decreased** estimated faithfulness by {abs(f_diff):.4f}.")
    else:
        lines.append("- GraphRAG had **no significant effect** on estimated faithfulness.")

    # Latency
    lat_rag = rag.get("avg_latency_ms", 0)
    lat_graph = graph.get("avg_latency_ms", 0)
    if lat_graph > lat_rag * 1.1:
        lines.append(f"- GraphRAG **increased** average latency from {lat_rag:.0f}ms to {lat_graph:.0f}ms.")
    elif lat_graph < lat_rag * 0.9:
        lines.append(f"- GraphRAG **decreased** average latency from {lat_rag:.0f}ms to {lat_graph:.0f}ms.")
    else:
        lines.append("- Latency was **similar** between the two modes.")

    lines.append("")
    lines.append("**Note:** These conclusions are based on automatic metrics. "
                 "If gold labels are TODO placeholders, retrieval recall will be 0 "
                 "and should not be interpreted as a real finding.")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="GraphResearcher RAG vs RAG+Graph ablation evaluation")
    parser.add_argument("--base-url", required=True, help="Base URL of running GraphResearcher backend")
    parser.add_argument("--document-id", required=True, help="Document ID to evaluate against")
    parser.add_argument("--qa-file", required=True, help="Path to QA JSONL file")
    parser.add_argument("--output-dir", default="reports/eval", help="Output directory for reports")
    parser.add_argument("--graph-entity-limit", type=int, default=12)
    parser.add_argument("--graph-retrieval-top-k", type=int, default=8)
    parser.add_argument("--allow-todo", action="store_true",
                        help="Allow running even if QA file has TODO values (Recall@K will be 0)")
    args = parser.parse_args()

    print(f"Loading QA file: {args.qa_file}")
    rows = load_qa_file(args.qa_file)
    print(f"Loaded {len(rows)} questions.")

    if has_todo_values(rows):
        if not args.allow_todo:
            print("\nERROR: QA file contains TODO values in gold_answer or relevant_chunk_ids.")
            print("Recall@K metrics will be meaningless with placeholder chunk IDs.")
            print("Fill in real gold labels first, or use --allow-todo to run anyway")
            print("(completeness and faithfulness will still be computed).")
            sys.exit(1)
        else:
            print("\nWARNING: QA file has TODO values. Recall@K will be 0. Running anyway (--allow-todo).")

    print(f"\n{'='*60}")
    print(f"Mode 1: RAG only")
    print(f"{'='*60}")
    rag_results = run_mode(
        args.base_url, args.document_id, rows,
        use_graph=False, use_graph_retrieval=False,
        graph_entity_limit=args.graph_entity_limit,
        graph_retrieval_top_k=args.graph_retrieval_top_k,
        mode_label="RAG",
    )

    print(f"\n{'='*60}")
    print(f"Mode 2: RAG + Graph")
    print(f"{'='*60}")
    graph_results = run_mode(
        args.base_url, args.document_id, rows,
        use_graph=True, use_graph_retrieval=True,
        graph_entity_limit=args.graph_entity_limit,
        graph_retrieval_top_k=args.graph_retrieval_top_k,
        mode_label="RAG + Graph",
    )

    rag_agg = aggregate(rag_results)
    graph_agg = aggregate(graph_results)

    print(f"\n{'='*60}")
    print(f"Summary")
    print(f"{'='*60}")
    print(f"RAG:         {rag_agg}")
    print(f"RAG + Graph: {graph_agg}")

    write_reports(rag_results, graph_results, rag_agg, graph_agg, args.output_dir, args.qa_file)


if __name__ == "__main__":
    main()
