import json
from unittest.mock import patch

import pytest

from backend.ai.question_generator import generate_questions


def _complete_exam():
    return [
        {
            "type": "multiple_choice",
            "question": "Choice one?",
            "options": ["A", "B", "C", "D"],
            "correct_answer": "A"
        },
        {
            "type": "multiple_choice",
            "question": "Choice two?",
            "options": ["A", "B", "C", "D"],
            "correct_answer": "B"
        },
        {
            "type": "true_false",
            "question": "True or false?",
            "correct_answer": "True"
        },
        {
            "type": "true_false",
            "question": "True or false?",
            "correct_answer": "False"
        },
        {
            "type": "open",
            "question": "Explain why?",
            "keywords": ["first", "second", "third"]
        }
    ]


def test_generate_questions_returns_required_mix_of_five():
    with patch(
        "ai.question_generator.ask_qwen",
        return_value={
            "success": True,
            "content": json.dumps(_complete_exam())
        }
    ):
        questions = generate_questions("Article text")

    assert len(questions) == 5
    assert [question["type"] for question in questions].count(
        "multiple_choice"
    ) == 2
    assert [question["type"] for question in questions].count("true_false") == 2
    assert [question["type"] for question in questions].count("open") == 1


def test_generation_prompt_covers_long_form_yki_reading_skills():
    with patch(
        "ai.question_generator.ask_qwen",
        return_value={
            "success": True,
            "content": json.dumps(_complete_exam())
        }
    ) as ask_qwen:
        generate_questions("Article text")

    prompt = ask_qwen.call_args.args[0]
    assert "main idea" in prompt
    assert "author's opinion" in prompt
    assert "inference" in prompt
    assert "writer's purpose" in prompt


def test_generate_questions_enforces_category_distribution_and_open_answer():
    questions = [
        {
            "type": "open",
            "question": f"Open question {index}?",
            "correct_answer": f"Model answer {index}.",
            "keywords": ["first", "second", "third"]
        }
        for index in range(1, 6)
    ]
    with patch(
        "ai.question_generator.ask_qwen",
        return_value={
            "success": True,
            "content": json.dumps(questions)
        }
    ) as ask_qwen:
        generated = generate_questions(
            "Long article",
            question_distribution={"open": 5},
            require_open_answer=True
        )

    assert len(generated) == 5
    assert all(question["correct_answer"] for question in generated)
    assert "main idea" in ask_qwen.call_args.args[0]

    questions[0]["correct_answer"] = ""
    with patch(
        "ai.question_generator.ask_qwen",
        return_value={
            "success": True,
            "content": json.dumps(questions)
        }
    ):
        assert generate_questions(
            "Long article",
            question_distribution={"open": 5},
            require_open_answer=True
        ) == []


def test_generate_questions_rejects_invalid_distribution():
    with pytest.raises(ValueError, match="valid question type distribution"):
        generate_questions(
            "Article",
            question_distribution={"unknown": 2}
        )


def test_generate_questions_rejects_wrong_question_count():
    with patch(
        "ai.question_generator.ask_qwen",
        return_value={"success": True, "content": "[]"}
    ):
        assert generate_questions("Article text") == []


@pytest.mark.parametrize(
    "invalid_exam",
    [
        None,
        [None, *_complete_exam()[1:]],
        [{**_complete_exam()[0], "type": "unsupported"}, *_complete_exam()[1:]],
        [{**_complete_exam()[0], "question": ""}, *_complete_exam()[1:]],
        [{**_complete_exam()[0], "options": ["A"]}, *_complete_exam()[1:]],
        [
            {**_complete_exam()[0], "correct_answer": "missing"},
            *_complete_exam()[1:]
        ],
        [
            *_complete_exam()[:2],
            {**_complete_exam()[2], "correct_answer": "sometimes"},
            *_complete_exam()[3:]
        ],
        [
            *_complete_exam()[:4],
            {**_complete_exam()[4], "keywords": ["only", "two"]}
        ],
        [
            *_complete_exam()[:2],
            {**_complete_exam()[2], "type": "multiple_choice"},
            *_complete_exam()[3:]
        ],
        [
            {**question, "type": "multiple_choice"}
            for question in _complete_exam()
        ]
    ]
)
def test_generate_questions_rejects_invalid_question_schemas(invalid_exam):
    with patch(
        "ai.question_generator.ask_qwen",
        return_value={
            "success": True,
            "content": json.dumps(invalid_exam)
        }
    ):
        assert generate_questions("Article text") == []


def test_generate_questions_reports_api_and_json_failures():
    with patch(
        "ai.question_generator.ask_qwen",
        return_value={"success": False, "error": "offline"}
    ):
        assert generate_questions("Article text") == []


def test_generate_questions_rejects_wrong_question_type_distribution():
    invalid_distribution = [
        {
            "type": "multiple_choice",
            "question": f"Choice {index}?",
            "options": ["A", "B", "C", "D"],
            "correct_answer": "A"
        }
        for index in range(5)
    ]
    with patch(
        "ai.question_generator.ask_qwen",
        return_value={
            "success": True,
            "content": json.dumps(invalid_distribution)
        }
    ):
        assert generate_questions("Article text") == []

    with patch(
        "ai.question_generator.ask_qwen",
        return_value={"success": True, "content": "not json"}
    ):
        assert generate_questions("Article text") == []

    with patch(
        "ai.question_generator.ask_qwen",
        return_value={"success": True, "content": None}
    ):
        assert generate_questions("Article text") == []
