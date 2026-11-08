import json

from backend.ai.model import ask_qwen

DEFAULT_DISTRIBUTION = {
    "multiple_choice": 2,
    "true_false": 2,
    "open": 1
}


def generate_questions(
        article_content: str,
        question_distribution: dict[str, int] | None = None,
        require_open_answer: bool = False
) -> list:
    expected_counts = question_distribution or DEFAULT_DISTRIBUTION
    valid_types = {"multiple_choice", "true_false", "open"}
    if (
        not expected_counts
        or set(expected_counts) - valid_types
        or any(
            not isinstance(count, int) or count < 0
            for count in expected_counts.values()
        )
        or not sum(expected_counts.values())
    ):
        raise ValueError("Provide a valid question type distribution.")
    if question_distribution is None or expected_counts == {"open": 5}:
        question_focus = (
            "The five long-form questions should collectively test the main "
            "idea, the author's opinion, inference, and the writer's purpose."
        )
    elif expected_counts == {"multiple_choice": 4}:
        question_focus = (
            "Test the notice's practical purpose, dates or locations, "
            "eligibility, and required action."
        )
    elif expected_counts == {"true_false": 4}:
        question_focus = (
            "Test factual details, instructions, conditions, and next steps "
            "stated in the email, letter, or guide."
        )
    else:
        question_focus = (
            "Cover the main idea, author opinion, inference, and writer's "
            "purpose when appropriate for the selected article."
        )

    prompt = f"""
You are an expert Finnish YKI Reading Exam creator.

Create EXACTLY {sum(expected_counts.values())} questions from the article.

Requirements:

{chr(10).join(
    f"- Create {count} {question_type} question(s)."
    for question_type, count in expected_counts.items()
    if count
)}

Every multiple_choice question must have exactly four options and exactly one
correct_answer matching one option. Every true_false question must have
correct_answer "True" or "False". Every open question must have 3-5 keywords
for automatic scoring and a concise explanation.
{"Every open question must also include a concise model answer in correct_answer." if require_open_answer else ""}

{question_focus}
Base every answer and explanation only on the article. Avoid questions that
can be answered from general knowledge alone.

Return ONLY valid JSON.

Example:

[
    {{
        "type": "multiple_choice",
        "question": "What is the main topic?",
        "options": [
            "Technology",
            "Health",
            "Sports",
            "Education"
        ],
        "correct_answer": "Technology",
        "explanation": "The article discusses technology."
    }},
    {{
        "type": "true_false",
        "question": "The article is about sports.",
        "correct_answer": "False",
        "explanation": "The article discusses technology."
    }},
    {{
        "type": "open",
        "question": "Why was the new policy introduced?",
        "correct_answer": "It was introduced to reduce traffic and emissions.",
        "keywords": [
            "traffic",
            "environment",
            "emissions"
        ],
        "explanation": "Reducing traffic and emissions."
    }}
]

Article:

{article_content}
"""

    response = ask_qwen(prompt)

    if not response["success"]:
        return []

    response_content = response.get("content")
    if not isinstance(response_content, str):
        return []

    content = response_content.replace("```json", "").replace("```", "").strip()

    try:
        questions = json.loads(
            content
        )
    except json.JSONDecodeError:
        return []

    if (
        not isinstance(questions, list)
        or len(questions) != sum(expected_counts.values())
    ):
        return []

    actual_counts = {question_type: 0 for question_type in expected_counts}

    for question in questions:
        if not isinstance(question, dict):
            return []

        question_type = question.get("type")
        if (
            not isinstance(question_type, str)
            or question_type not in expected_counts
        ):
            return []

        if not isinstance(question.get("question"), str) or not question["question"].strip():
            return []

        actual_counts[question_type] += 1

        if question_type == "multiple_choice":
            options = question.get("options")
            correct_answer = question.get("correct_answer")
            if (
                not isinstance(options, list)
                or len(options) != 4
                or not all(isinstance(option, str) and option.strip() for option in options)
                or correct_answer not in options
            ):
                return []

        elif question_type == "true_false":
            answer = str(question.get("correct_answer", "")).strip().lower()
            if answer not in {"true", "false"}:
                return []
            question["correct_answer"] = answer.title()

        else:
            keywords = question.get("keywords")
            if (
                not isinstance(keywords, list)
                or not 3 <= len(keywords) <= 5
                or not all(isinstance(keyword, str) and keyword.strip() for keyword in keywords)
            ):
                return []
            if require_open_answer and (
                not isinstance(question.get("correct_answer"), str)
                or not question["correct_answer"].strip()
            ):
                return []

    if actual_counts != expected_counts:
        return []

    return questions