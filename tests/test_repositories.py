import json
from contextlib import closing

import pytest

from models.article import Article
from models.exam_result import ExamResult
from models.question import Question
from models.user_answer import UserAnswer
from repositories.article_repository import ArticleRepository
from repositories.exam_result_repository import ExamResultRepository
from repositories.question_repository import QuestionRepository
from repositories.user_answer_repository import UserAnswerRepository
from repositories.vocabulary_repository import VocabularyRepository


def make_article():
    return Article(
        id=None,
        title="Etätyö Suomessa",
        source="News",
        content="Etätyö on yleistynyt.",
        detected_level="B1",
        level_confidence=0.8,
        subject="Work",
        subject_confidence=0.9,
        word_count=3
    )


def save_approved_article(article=None):
    return ArticleRepository.save_approved_exam_article(
        article or make_article(),
        rights_basis="CC BY 4.0, reuse permitted",
        permission_reference="https://example.test/license",
        approved_by="thesis supervisor"
    )


def test_article_repository_saves_and_gets_random_article(database):
    article_id = save_approved_article()

    article = ArticleRepository.get_random_article()
    assert article is None

    QuestionRepository.save_all(article_id, [{
        "type": "true_false",
        "question": "Onko etätyö yleistä?",
        "correct_answer": "True"
    }])

    article = ArticleRepository.get_random_article()
    assert article.id == article_id
    assert article.detected_level == "B1"
    assert article.subject == "Work"


def test_question_repository_saves_reads_in_order_and_preserves_unicode(database):
    article_id = save_approved_article()
    QuestionRepository.save_all(article_id, [
        {
            "type": "open",
            "question": "Miksi?",
            "keywords": ["työ", "koti", "Suomi"]
        },
        {
            "type": "true_false",
            "question": "Totta?",
            "correct_answer": "True"
        }
    ])

    questions = QuestionRepository.find_by_article_id(article_id)
    assert [question.question_no for question in questions] == [1, 2]
    assert json.loads(questions[0].keywords) == ["työ", "koti", "Suomi"]
    assert questions[1].correct_answer == "True"


def test_vocabulary_repository_saves_and_updates_word_analysis(database):
    article_id = save_approved_article()
    analysis = VocabularyRepository.save_word_analysis(
        word_form="kotona",
        lemma="koti",
        part_of_speech="noun",
        meaning="home; at home",
        noun_type="countable",
        suffixes=[{"suffix": "na", "function": "essive"}],
        grammatical_features={"case": "essive", "number": "singular"},
        stem_changes=["final i becomes e before the essive suffix"],
        word_forms=[
            {
                "grammatical_case": "partitive",
                "number": "singular",
                "form": "kotia"
            },
            {
                "grammatical_case": "partitive",
                "number": "plural",
                "form": "kotoja"
            }
        ],
        subject="Work",
        article_id=article_id
    )

    saved = VocabularyRepository.get_word_analysis(
        " KOTI ",
        article_id=article_id
    )

    assert {
        key: value
        for key, value in saved.items()
        if key != "forms"
    } == {
        key: value
        for key, value in analysis.items()
        if key != "forms"
    }
    assert {
        (form["grammatical_case"], form["number"], form["form"])
        for form in saved["forms"]
    } == {
        ("partitive", "singular", "kotia"),
        ("partitive", "plural", "kotoja")
    }

    updated = VocabularyRepository.save_word_analysis(
        word_form="kotiin",
        lemma="KOTI",
        part_of_speech="noun",
        meaning="home; to home",
        noun_type="countable",
        suffixes=[{"suffix": "in", "function": "illative"}],
        grammatical_features={"case": "illative"},
        subject="Work",
        article_id=article_id
    )

    assert updated["id"] == analysis["id"]
    assert VocabularyRepository.get_word_analysis(
        "koti",
        article_id=article_id
    )["grammatical_features"] == {"case": "illative"}
    assert {
        (form["grammatical_case"], form["number"], form["form"])
        for form in VocabularyRepository.get_word_analysis(
            "koti",
            article_id=article_id
        )["forms"]
    } == {
        ("partitive", "singular", "kotia"),
        ("partitive", "plural", "kotoja")
    }


def test_result_and_answer_repositories_persist_exam(database):
    article_id = save_approved_article()
    QuestionRepository.save_all(article_id, [{
        "type": "true_false",
        "question": "True?",
        "correct_answer": "True"
    }])
    question = QuestionRepository.find_by_article_id(article_id)[0]

    result_id = ExamResultRepository.save(ExamResult(
        id=None,
        article_id=article_id,
        score=100,
        correct_answers=1,
        total_questions=1
    ))
    UserAnswerRepository.save_all([UserAnswer(
        id=None,
        exam_result_id=result_id,
        question_id=question.id,
        selected_answer="True",
        is_correct=True
    )])

    with closing(database()) as connection:
        result = connection.execute(
            "SELECT score, correct_answers, total_questions FROM exam_results WHERE id = ?",
            (result_id,)
        ).fetchone()
        answer = connection.execute(
            "SELECT selected_answer, is_correct FROM user_answers WHERE exam_result_id = ?",
            (result_id,)
        ).fetchone()

    assert result == (100.0, 1, 1)
    assert answer == ("True", 1)


def test_only_approved_articles_are_eligible_for_random_exam(database):
    article_id = save_approved_article()
    with closing(database()) as connection:
        connection.execute("""
            INSERT INTO articles (
                title, source, content, detected_level, subject,
                reuse_approved
            )
            VALUES ('Unapproved', 'User', 'Private text', 'B1', 'Work', 0)
        """)
        connection.commit()
        unapproved_id = connection.execute(
            "SELECT id FROM articles WHERE title = 'Unapproved'"
        ).fetchone()[0]

    QuestionRepository.save_all(article_id, [{
        "type": "true_false",
        "question": "Approved?",
        "correct_answer": "True"
    }])
    with pytest.raises(ValueError, match="approved exam library"):
        QuestionRepository.save_all(unapproved_id, [{
            "type": "true_false",
            "question": "Unapproved?",
            "correct_answer": "True"
        }])

    selected = ArticleRepository.get_random_article()
    assert selected.id == article_id


def test_exam_library_requires_rights_basis_and_approval(database):
    with pytest.raises(ValueError, match="permission_reference"):
        ArticleRepository.save_approved_exam_article(
            make_article(),
            rights_basis="CC BY",
            permission_reference=" ",
            approved_by="reviewer"
        )
