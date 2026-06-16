from pathlib import Path

# Remove BOM from Python files
for path in Path("app").rglob("*.py"):
    text = path.read_text(encoding="utf-8-sig")
    text = text.replace("\ufeff", "")
    path.write_text(text, encoding="utf-8")

print("BOM cleanup completed.")


# =====================================================
# 1. Shared graph quality filters
# =====================================================

Path("app/graph/graph_quality.py").write_text(r'''
import re
from typing import Any


BAD_ENTITY_NAMES = {
    "what", "why", "when", "where", "who", "how",
    "is", "are", "was", "were", "be", "been", "being",
    "this", "that", "these", "those", "it", "they", "them",
    "page", "chapter", "section", "paragraph", "figure", "table",
    "contents", "overview", "summary", "introduction", "conclusion",
    "question", "answer", "example", "note", "notes",
    "part", "step", "case", "item", "level", "scope"
}


BAD_SINGLE_WORDS = BAD_ENTITY_NAMES | {
    "one", "two", "three", "first", "second", "third",
    "good", "bad", "new", "old", "main", "basic", "advanced"
}


def get_value(obj: Any, key: str, default=None):
    if isinstance(obj, dict):
        return obj.get(key, default)

    return getattr(obj, key, default)


def normalize_name(name: str) -> str:
    return re.sub(r"\s+", " ", str(name or "")).strip()


def tokenize_name(name: str):
    return re.findall(r"[a-zA-Z0-9_]+", str(name or "").lower())


def is_noisy_entity_name(name: str) -> bool:
    name = normalize_name(name)

    if not name:
        return True

    name_lower = name.lower()
    tokens = tokenize_name(name)

    if name_lower in BAD_ENTITY_NAMES:
        return True

    if len(tokens) == 1 and tokens[0] in BAD_SINGLE_WORDS:
        return True

    if len(name) <= 1:
        return True

    # Very short uppercase words like IS, OR, TO are usually not entities.
    # Keep useful acronyms like RAG, LLM, API, OCR, SQL, NLP, BM25.
    useful_acronyms = {"rag", "llm", "api", "ocr", "sql", "nlp", "bm25", "gpt", "pdf", "mvp"}

    if name.isupper() and len(name) <= 3 and name_lower not in useful_acronyms:
        return True

    if name_lower.startswith("chapter ") and len(tokens) <= 4:
        return True

    if name_lower.startswith("page ") and len(tokens) <= 4:
        return True

    return False


def is_noisy_relation(relation: Any) -> bool:
    source = get_value(relation, "source_name") or get_value(relation, "source")
    target = get_value(relation, "target_name") or get_value(relation, "target")
    relation_type = str(get_value(relation, "relation_type", "")).upper()

    if is_noisy_entity_name(source):
        return True

    if is_noisy_entity_name(target):
        return True

    # IS_A from rule-based extraction is noisy unless both sides look meaningful.
    if relation_type == "IS_A":
        target_tokens = tokenize_name(target)

        if len(target_tokens) == 1 and target_tokens[0] in BAD_SINGLE_WORDS:
            return True

    return False


def is_low_quality_chunk_text(text: str) -> bool:
    text = str(text or "").strip()

    if not text:
        return True

    lower = text.lower()
    dot_leaders = len(re.findall(r"\.{5,}", text))
    words = re.findall(r"[a-zA-Z]{3,}", text)

    # Table-of-content pages often contain many dot leaders.
    if dot_leaders >= 3:
        return True

    if "table of contents" in lower and dot_leaders >= 1:
        return True

    # Mostly heading/index text, not answer evidence.
    heading_markers = [
        "chapter ",
        "page ",
        "................................................................"
    ]

    marker_count = sum(1 for marker in heading_markers if marker in lower)

    if marker_count >= 2 and len(words) < 90:
        return True

    return False
''', encoding="utf-8")


# =====================================================
# 2. Improve entity extractor
# =====================================================

Path("app/graph/entity_extractor.py").write_text(r'''
import re
from typing import List, Dict, Any

from app.graph.graph_quality import is_noisy_entity_name


STOP_ENTITIES = {
    "The", "This", "That", "These", "Those", "It", "They", "We", "You",
    "Page", "Chapter", "Figure", "Table", "Example", "Answer", "Question",
    "Introduction", "Conclusion", "Summary", "Overview", "Paragraph",
    "What", "Why", "When", "Where", "Who", "How", "Is", "Are", "IS"
}


def normalize_entity_name(name: str) -> str:
    name = re.sub(r"\s+", " ", name or "").strip()
    name = name.strip(".,;:()[]{}")
    return name


def make_entity_id(name: str) -> str:
    cleaned = name.lower()
    cleaned = re.sub(r"[^a-z0-9]+", "_", cleaned)
    cleaned = cleaned.strip("_")
    return cleaned[:80] or "unknown_entity"


def classify_entity(name: str) -> str:
    if re.fullmatch(r"[A-Z][A-Z0-9]{1,9}", name):
        return "ACRONYM"

    org_markers = [
        "University", "Institute", "Corporation", "Corp", "Inc", "Ltd",
        "Company", "OpenAI", "Microsoft", "Google", "Amazon"
    ]

    if any(marker.lower() in name.lower() for marker in org_markers):
        return "ORGANIZATION"

    if any(char.isdigit() for char in name):
        return "TECHNICAL_TERM"

    if "-" in name or "/" in name:
        return "TECHNICAL_TERM"

    return "CONCEPT"


def is_valid_entity(name: str) -> bool:
    if not name:
        return False

    if name in STOP_ENTITIES:
        return False

    if is_noisy_entity_name(name):
        return False

    if len(name) < 2:
        return False

    if len(name) > 90:
        return False

    return True


def extract_entities_from_text(text: str) -> List[Dict[str, Any]]:
    if not text:
        return []

    candidates = []

    # Acronyms like RAG, LLM, API, OCR, BM25
    for match in re.finditer(r"\b[A-Z][A-Z0-9]{1,9}\b", text):
        candidates.append(match.group(0))

    # Capitalized technical phrases like Retrieval-Augmented Generation
    capitalized_phrase_pattern = (
        r"\b[A-Z][a-zA-Z0-9]*(?:[-/][A-Z]?[a-zA-Z0-9]+)?"
        r"(?:\s+[A-Z][a-zA-Z0-9]*(?:[-/][A-Z]?[a-zA-Z0-9]+)?){0,5}\b"
    )

    for match in re.finditer(capitalized_phrase_pattern, text):
        candidates.append(match.group(0))

    cleaned_entities = []
    seen = set()

    for candidate in candidates:
        name = normalize_entity_name(candidate)

        if not is_valid_entity(name):
            continue

        entity_id = make_entity_id(name)

        if entity_id in seen:
            continue

        seen.add(entity_id)

        cleaned_entities.append(
            {
                "entity_id": entity_id,
                "name": name,
                "entity_type": classify_entity(name)
            }
        )

    return cleaned_entities


def split_sentences(text: str) -> List[str]:
    if not text:
        return []

    parts = re.split(r"(?<=[.!?])\s+", text)
    return [part.strip() for part in parts if len(part.strip()) > 20]
''', encoding="utf-8")


# =====================================================
# 3. Improve relation extractor
# =====================================================

Path("app/graph/relation_extractor.py").write_text(r'''
import itertools
import re
from typing import List, Dict, Any

from app.graph.entity_extractor import split_sentences
from app.graph.graph_quality import is_noisy_entity_name


VERB_RELATION_MAP = {
    "stands for": "STANDS_FOR",
    "refers to": "REFERS_TO",
    "uses": "USES",
    "use": "USES",
    "retrieves": "RETRIEVES",
    "retrieve": "RETRIEVES",
    "generates": "GENERATES",
    "generate": "GENERATES",
    "provides": "PROVIDES",
    "provide": "PROVIDES",
    "reduces": "REDUCES",
    "reduce": "REDUCES",
    "improves": "IMPROVES",
    "improve": "IMPROVES",
    "contains": "CONTAINS",
    "include": "INCLUDES",
    "includes": "INCLUDES"
}


def relation_id(source_id: str, relation_type: str, target_id: str) -> str:
    return f"{source_id}__{relation_type.lower()}__{target_id}"[:160]


def entity_appears_in_sentence(entity_name: str, sentence: str) -> bool:
    pattern = r"\b" + re.escape(entity_name) + r"\b"
    return re.search(pattern, sentence, flags=re.IGNORECASE) is not None


def extract_relations_from_text(
    text: str,
    entities: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:

    if not text or len(entities) < 2:
        return []

    relations = []
    sentences = split_sentences(text)

    clean_entities = [
        entity for entity in entities
        if not is_noisy_entity_name(entity.get("name", ""))
    ]

    if len(clean_entities) < 2:
        return []

    for sentence in sentences:
        present_entities = [
            entity for entity in clean_entities
            if entity_appears_in_sentence(entity["name"], sentence)
        ]

        # Avoid relation explosion
        present_entities = present_entities[:5]

        if len(present_entities) < 2:
            continue

        relation_type = detect_relation_type(sentence)

        for source, target in itertools.combinations(present_entities, 2):
            if source["entity_id"] == target["entity_id"]:
                continue

            if is_noisy_entity_name(source["name"]) or is_noisy_entity_name(target["name"]):
                continue

            relations.append(
                {
                    "relation_id": relation_id(
                        source["entity_id"],
                        relation_type,
                        target["entity_id"]
                    ),
                    "source_entity_id": source["entity_id"],
                    "target_entity_id": target["entity_id"],
                    "source_name": source["name"],
                    "target_name": target["name"],
                    "relation_type": relation_type,
                    "evidence_sentence": sentence
                }
            )

    return relations


def detect_relation_type(sentence: str) -> str:
    sentence_lower = sentence.lower()

    for phrase, relation_type in VERB_RELATION_MAP.items():
        if phrase in sentence_lower:
            return relation_type

    return "RELATED_TO"
''', encoding="utf-8")


# =====================================================
# 4. Improve graph context filtering
# =====================================================

Path("app/graph/graph_context_service.py").write_text(r'''
import re
from typing import Dict, Any, List, Optional

from app.graph.graph_storage import read_document_graph
from app.graph.graph_quality import is_noisy_entity_name, is_noisy_relation


STOPWORDS = {
    "what", "is", "are", "the", "a", "an", "of", "to", "and", "or",
    "in", "on", "for", "with", "from", "by", "how", "why", "explain",
    "define", "meaning", "does", "do", "it", "this", "that"
}


def tokenize_query(query: str) -> List[str]:
    words = re.findall(r"[a-zA-Z0-9_]+", (query or "").lower())

    return [
        word for word in words
        if word not in STOPWORDS and len(word) > 1
    ]


def tokenize_entity_name(name: str) -> List[str]:
    return re.findall(r"[a-zA-Z0-9_]+", (name or "").lower())


def entity_relevance_score(entity, query_terms: List[str]) -> float:
    if not query_terms:
        return 0.0

    if is_noisy_entity_name(entity.name):
        return 0.0

    name_lower = entity.name.lower()
    entity_id_lower = entity.entity_id.lower()
    name_tokens = tokenize_entity_name(entity.name)
    entity_id_tokens = tokenize_entity_name(entity.entity_id.replace("_", " "))

    score = 0.0

    for term in query_terms:
        if term == name_lower or term == entity_id_lower:
            score += 10.0
            continue

        if term in name_tokens:
            score += 6.0
            continue

        if term in entity_id_tokens:
            score += 5.0
            continue

        # Avoid rag matching paragraph. Substring only for longer terms.
        if len(term) >= 4 and term in name_lower:
            score += 2.0

    if score > 0:
        score += min(entity.mention_count, 10) * 0.15

    return score


def build_graph_context_for_query(
    document_id: Optional[str],
    query: str,
    limit: int = 8
) -> Dict[str, Any]:

    if not document_id:
        return {
            "graph_available": False,
            "reason": "No document_id provided.",
            "matched_entities": [],
            "matched_relations": [],
            "context_text": ""
        }

    graph = read_document_graph(document_id)

    if graph is None:
        return {
            "graph_available": False,
            "reason": "Graph not built for this document.",
            "matched_entities": [],
            "matched_relations": [],
            "context_text": ""
        }

    query_terms = tokenize_query(query)

    scored_entities = []

    for entity in graph.entities:
        score = entity_relevance_score(entity, query_terms)

        if score > 0:
            scored_entities.append((score, entity))

    scored_entities.sort(key=lambda item: item[0], reverse=True)

    matched_entities = [
        entity for score, entity in scored_entities[:limit]
    ]

    matched_entity_ids = {
        entity.entity_id for entity in matched_entities
    }

    matched_relations = []

    for relation in graph.relations:
        if is_noisy_relation(relation):
            continue

        if (
            relation.source_entity_id in matched_entity_ids
            or relation.target_entity_id in matched_entity_ids
        ):
            matched_relations.append(relation)

    matched_relations = sorted(
        matched_relations,
        key=lambda relation: relation.weight,
        reverse=True
    )[:limit]

    context_text = build_graph_context_text(
        matched_entities=matched_entities,
        matched_relations=matched_relations
    )

    return {
        "graph_available": True,
        "document_id": document_id,
        "source_file_name": graph.source_file_name,
        "query_terms": query_terms,
        "matched_entities": [
            {
                "entity_id": entity.entity_id,
                "name": entity.name,
                "entity_type": entity.entity_type,
                "mention_count": entity.mention_count,
                "pages": entity.pages[:10],
                "chunk_ids": entity.chunk_ids[:10]
            }
            for entity in matched_entities
        ],
        "matched_relations": [
            {
                "relation_id": relation.relation_id,
                "source": relation.source_name,
                "relation_type": relation.relation_type,
                "target": relation.target_name,
                "weight": relation.weight,
                "pages": relation.pages[:10],
                "chunk_ids": relation.chunk_ids[:10]
            }
            for relation in matched_relations
        ],
        "context_text": context_text
    }


def build_graph_context_text(
    matched_entities,
    matched_relations
) -> str:
    lines = []

    if matched_entities:
        lines.append("Relevant graph entities:")

        for entity in matched_entities:
            pages = ", ".join(str(page) for page in entity.pages[:5])
            lines.append(
                f"- {entity.name} ({entity.entity_type}), mentions={entity.mention_count}, pages={pages}"
            )

    if matched_relations:
        lines.append("")
        lines.append("Relevant graph relations:")

        for relation in matched_relations:
            lines.append(
                f"- {relation.source_name} --{relation.relation_type}--> {relation.target_name} "
                f"(weight={relation.weight})"
            )

    return "\n".join(lines).strip()
''', encoding="utf-8")


# =====================================================
# 5. Improve graph-guided retrieval
# =====================================================

retriever_path = Path("app/graph/graph_guided_retriever.py")
text = retriever_path.read_text(encoding="utf-8-sig")
text = text.replace("\ufeff", "")

if "from app.graph.graph_quality import is_low_quality_chunk_text" not in text:
    text = text.replace(
        "from app.storage.processed_storage import read_processed_chunks",
        "from app.storage.processed_storage import read_processed_chunks\nfrom app.graph.graph_quality import is_low_quality_chunk_text"
    )

old = '''        results.append(
            {
                "rank": rank,
                "chunk_id": chunk_id,
                "graph_score": round(info["score"], 4),
                "page_number": get_value(chunk, "page_number"),
                "source_file_name": (
                    get_value(chunk, "source_file_name")
                    or get_value(chunk, "file_name")
                    or get_value(chunk, "filename")
                ),
                "matched_entities": sorted(set(info["matched_entities"])),
                "matched_relations": sorted(set(info["matched_relations"])),
                "text_preview": extract_text_preview(chunk)
            }
        )
'''

new = '''        text_preview = extract_text_preview(chunk)

        if is_low_quality_chunk_text(text_preview):
            continue

        results.append(
            {
                "rank": len(results) + 1,
                "chunk_id": chunk_id,
                "graph_score": round(info["score"], 4),
                "page_number": get_value(chunk, "page_number"),
                "source_file_name": (
                    get_value(chunk, "source_file_name")
                    or get_value(chunk, "file_name")
                    or get_value(chunk, "filename")
                ),
                "matched_entities": sorted(set(info["matched_entities"])),
                "matched_relations": sorted(set(info["matched_relations"])),
                "text_preview": text_preview
            }
        )
'''

if old in text:
    text = text.replace(old, new)
else:
    print("Graph retriever append block not found. It may already be patched.")

retriever_path.write_text(text, encoding="utf-8")

print("Phase 18 graph quality cleanup applied.")
