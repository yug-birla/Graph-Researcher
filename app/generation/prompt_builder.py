from app.generation.question_classifier import get_answer_instruction


def build_grounded_prompt(
    query: str,
    evidence_context: str,
    question_type: str
) -> str:
    """
    Builds a compact prompt.

    Small local models perform better with short, direct prompts.
    """

    instruction = get_answer_instruction(question_type)

    return f"""
Answer the question using only the evidence.

Question type: {question_type}

Instruction: {instruction}

Rules:
- Do not use outside knowledge.
- Do not mention missing information unless evidence is missing.
- Use citations like [S1] and [S2].
- Give a clear final answer, not notes.

Question:
{query}

Evidence:
{evidence_context}

Final answer:
""".strip()
