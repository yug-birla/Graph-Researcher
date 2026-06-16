from typing import Literal


QuestionType = Literal[
    "definition",
    "summary",
    "comparison",
    "steps",
    "reason",
    "general"
]


def classify_question(query: str) -> QuestionType:
    query_lower = query.lower().strip()

    if query_lower.startswith("what is") or query_lower.startswith("what are"):
        return "definition"

    if query_lower.startswith("define") or "meaning of" in query_lower:
        return "definition"

    if "summarize" in query_lower or "summary" in query_lower:
        return "summary"

    if "compare" in query_lower or "difference between" in query_lower or "vs" in query_lower:
        return "comparison"

    if query_lower.startswith("how to") or "steps" in query_lower or "step by step" in query_lower:
        return "steps"

    if query_lower.startswith("why") or "reason" in query_lower:
        return "reason"

    return "general"


def get_answer_instruction(question_type: QuestionType) -> str:
    if question_type == "definition":
        return (
            "Give a clear definition first. Then explain why it matters. "
            "Keep the answer short and cite the evidence."
        )

    if question_type == "summary":
        return (
            "Give a concise structured summary using the most important points. "
            "Avoid unnecessary details and cite sources."
        )

    if question_type == "comparison":
        return (
            "Compare the concepts clearly. Mention similarities, differences, "
            "and practical implications. Cite sources."
        )

    if question_type == "steps":
        return (
            "Explain the answer as clear steps. Keep each step simple. Cite sources."
        )

    if question_type == "reason":
        return (
            "Explain the reason logically using evidence from the sources. Cite sources."
        )

    return (
        "Answer clearly using only the retrieved sources. Cite the evidence."
    )
