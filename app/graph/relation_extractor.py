
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
