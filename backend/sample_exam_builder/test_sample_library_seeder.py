import json
import sqlite3
from unittest.mock import patch

import pytest

from backend.database import init_db as database_init
from backend.repositories import article_ingestion_repository, article_repository
from backend.repositories import (
    question_repository
)
from backend.repositories.article_ingestion_repository import (
    ArticleIngestionRepository
)
from backend.repositories.question_repository import QuestionRepository
from backend.sample_exam_builder.seeder import (
    _generate_batch,
    _save_generated_article,
    _validate_questions,
    _word_count
)


@pytest.fixture
def database(tmp_path, monkeypatch):
    database_path = tmp_path / "test_yki.db"

    def connect():
        connection = sqlite3.connect(database_path)
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    monkeypatch.setattr(database_init, "get_connection", connect)
    monkeypatch.setattr(article_repository, "get_connection", connect)
    monkeypatch.setattr(
        article_ingestion_repository,
        "get_connection",
        connect
    )
    monkeypatch.setattr(question_repository, "get_connection", connect)
    database_init.init_db()
    return connect


def _notice_questions():
    return [
        {
            "type": "multiple_choice",
            "question": f"Notice question {index}?",
            "options": ["A", "B", "C", "D"],
            "correct_answer": "A",
            "explanation": "The notice states this."
        }
        for index in range(1, 5)
    ]


def test_seed_batch_validates_original_text_and_exact_word_range():
    content = " ".join(f"sana{index}" for index in range(35))
    articles = [{
        "number": index,
        "title": f"Alkuperäinen ilmoitus {index}",
        "content": content,
        "subject": "Everyday life",
        "questions": _notice_questions()
    } for index in range(1, 4)]

    with patch(
        "sample_exam_builder.seeder.ask_qwen",
        return_value={
            "success": True,
            "content": json.dumps(
                {"articles": articles},
                ensure_ascii=False
            )
        }
    ) as ask_qwen:
        generated = _generate_batch("notice", 1, 3)

    assert len(generated) == 3
    assert _word_count(generated[0]["content"]) == 35
    assert "not copied or adapted" in ask_qwen.call_args.args[0]


def test_seed_batch_rejects_text_outside_category_word_count():
    article = {
        "number": 1,
        "title": "Short notice",
        "content": "too few words",
        "subject": "Everyday life",
        "questions": _notice_questions()
    }
    with patch(
        "sample_exam_builder.seeder.ask_qwen",
        return_value={
            "success": True,
            "content": json.dumps({"articles": [article]})
        }
    ):
        with pytest.raises(ValueError, match="expected 20-100"):
            _generate_batch("notice", 1, 1)


def test_long_article_and_questions_are_generated_separately():
    article = {
        "title": "Kaupungin yhteinen puutarha",
        "content": " ".join(f"sana{index}" for index in range(293)),
        "subject": "Everyday life"
    }
    questions = [{
        "type": "open",
        "question": f"Mitä artikkelissa kerrotaan, kysymys {index}?",
        "correct_answer": "Puutarha auttaa asukkaita tapaamaan.",
        "explanation": "Artikkeli kertoo puutarhasta.",
        "keywords": ["puutarha", "asukkaat", "tapaaminen"]
    } for index in range(1, 6)]

    with patch(
        "sample_exam_builder.seeder.ask_qwen",
        side_effect=[
            {
                "success": True,
                "content": (
                    f"TITLE: {article['title']}\n"
                    f"SUBJECT: {article['subject']}\n"
                    f"CONTENT:\n{article['content']}"
                )
            },
            {
                "success": True,
                "content": " ".join(f"jatko{index}" for index in range(20))
            },
            {
                "success": True,
                "content": json.dumps(
                    {"questions": questions},
                    ensure_ascii=False
                )
            }
        ]
    ) as ask_qwen:
        generated = _generate_batch("utiset", 1, 1)

    assert len(generated) == 1
    assert _word_count(generated[0]["content"]) == 313
    assert len(generated[0]["questions"]) == 5
    assert "Do not include questions" in ask_qwen.call_args_list[0].args[0]
    assert article["content"] in ask_qwen.call_args_list[2].args[0]


def test_seed_question_validation_requires_open_answer_keys():
    invalid_questions = [{
        "type": "open",
        "question": "Why?",
        "correct_answer": "",
        "explanation": "Text evidence.",
        "keywords": ["first", "second", "third"]
    } for _ in range(5)]

    with pytest.raises(ValueError, match="no answer key"):
        _validate_questions("utiset", invalid_questions)


def test_seed_saves_article_questions_and_rights_provenance(database):
    content = " ".join(f"sana{index}" for index in range(40))
    article_data = {
        "number": 1,
        "title": "Alkuperäinen ilmoitus",
        "content": content,
        "subject": "Everyday life",
        "questions": _notice_questions()
    }

    article_id = _save_generated_article("notice", article_data)

    assert ArticleIngestionRepository.count_approved_articles("notice") == 1
    saved_questions = QuestionRepository.find_by_article_id(article_id)
    assert len(saved_questions) == 4
    assert all(
        question.question_type == "multiple_choice"
        and question.correct_answer == "A"
        for question in saved_questions
    )
