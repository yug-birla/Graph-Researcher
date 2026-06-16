
from app.generation.question_classifier import get_answer_instruction


def build_grounded_prompt(
    query: str,
    evidence_context: str,
    question_type: str
) -> str:
    """
    Builds a compact prompt.

    In Phase 15, evidence_context may contain:
    - retrieved source evidence
    - graph entity context
    - graph relation context

    The LLM still must answer only from supplied context.
    """

    instruction = get_answer_instruction(question_type)

    return f"""
Answer the question using only the supplied context.

Question type: {question_type}

Instruction: {instruction}

Rules:
- Do not use outside knowledge.
- Preserve citations like [S1] and [S2] when making factual claims from retrieved sources.
- Graph context can help explain entity relationships, but do not invent facts from it.
- If retrieved source evidence and graph context disagree, trust retrieved source evidence.
- Give a clear final answer, not notes.

Question:
{query}

Context:
{evidence_context}

Final answer:
""".strip()
