from contextlib import closing
from unittest.mock import patch

import pytest

from backend.ai_neural_networks.reading.models.article import Article
from backend.ai_neural_networks.reading.models.exam_category import EXAM_CATEGORY_RULES
from backend.ai_neural_networks.reading.models.question import Question
from backend.ai_neural_networks.reading.services import article_service
from backend.repositories.article_repository import ArticleRepository
from backend.repositories.question_repository import QuestionRepository
from backend.ai_neural_networks.reading.services import exam_service
from backend.ai_neural_networks.reading.services.ai_feedback_service import AIFeedbackService
from backend.ai_neural_networks.reading.services.exam_service import ExamService
from backend.ai_neural_networks.reading.services.score_service import ScoreService


def generated_questions():
    return [
        {
            "type": "multiple_choice",
            "question": "Q1?",
            "options": ["A", "B", "C", "D"],
            "correct_answer": "A"
        },
        {
            "type": "multiple_choice",
            "question": "Q2?",
            "options": ["A", "B", "C", "D"],
            "correct_answer": "B"
        },
        {
            "type": "true_false",
            "question": "Q3?",
            "correct_answer": "True"
        },
        {
            "type": "true_false",
            "question": "Q4?",
            "correct_answer": "False"
        },
        {
            "type": "open",
            "question": "Q5?",
            "keywords": ["työ", "koti", "Suomi"]
        }
    ]


def question(question_id, question_type, answer, keywords=None):
    return Question(
        id=question_id,
        article_id=10,
        question_no=question_id,
        question_type=question_type,
        question=f"Question {question_id}?",
        option_a="A",
        option_b="B",
        option_c="C",
        option_d="D",
        correct_answer=answer,
        keywords=keywords,
        explanation=None
    )


def test_article_service_validates_content_before_ai():
    for content in (None, "", "  "):
        with patch.object(article_service, "detect_level") as detect:
            result = article_service.ArticleService.process_article(
                content
            )

        assert result["success"] is False
        assert "content" in result["message"]
        detect.assert_not_called()


def test_article_service_processes_user_article_without_persisting(database):
    with (
        patch.object(
            article_service,
            "detect_level",
            return_value={"level": "B1", "confidence": 0.8}
        ),
        patch.object(
            article_service,
            "classify_subject",
            return_value={"subject": "Work", "confidence": 0.9}
        ),
        patch.object(
            article_service,
            "generate_questions",
            return_value=generated_questions()
        )
    ):
        result = article_service.ArticleService.process_article(
            "Etätyö on yleistynyt Suomessa."
        )

    assert result["success"] is True
    assert result["article_id"] is None
    assert len(result["questions"]) == 5
    assert all(question.id is None for question in result["questions"])
    with closing(database()) as connection:
        assert connection.execute(
            "SELECT COUNT(*) FROM articles"
        ).fetchone()[0] == 0
        assert connection.execute(
            "SELECT COUNT(*) FROM questions"
        ).fetchone()[0] == 0


@pytest.mark.parametrize(
    ("level_result", "subject_result", "questions", "expected_message"),
    [
        (
            {"level": None, "confidence": 0.0},
            {"subject": "Work", "confidence": 0.9},
            generated_questions(),
            "level"
        ),
        (
            {"level": "B1", "confidence": 0.8},
            {"subject": None, "confidence": 0.0},
            generated_questions(),
            "subject"
        ),
        (
            {"level": "B1", "confidence": 0.8},
            {"subject": "Work", "confidence": 0.9},
            [],
            "questions"
        )
    ]
)
def test_article_service_does_not_save_incomplete_analysis(
    level_result,
    subject_result,
    questions,
    expected_message
):
    with (
        patch.object(article_service, "detect_level", return_value=level_result),
        patch.object(article_service, "classify_subject", return_value=subject_result),
        patch.object(article_service, "generate_questions", return_value=questions),
    ):
        result = article_service.ArticleService.process_article(
            "Content"
        )

    assert result["success"] is False
    assert expected_message in result["message"].lower()


def test_exam_service_gets_random_exam_and_creates_questions(database):
    article_ids = []
    for category, rules in EXAM_CATEGORY_RULES.items():
        article_id = ArticleRepository.save_approved_exam_article(
            Article(
                id=None,
                title=category,
                source="Licensed source",
                content="Licensed text",
                detected_level=rules["target_level"] or "B1",
                level_confidence=0.8,
                subject="Work",
                subject_confidence=0.9,
                word_count=50,
                exam_category=category
            ),
            rights_basis="CC BY 4.0",
            permission_reference="https://example.test/license",
            approved_by="reviewer",
            exam_category=category
        )
        article_ids.append(article_id)
        question_distribution = rules["question_distribution"]
        questions = []
        for question_type, count in question_distribution.items():
            for index in range(count):
                question = {
                    "type": question_type,
                    "question": f"{category} question {index + 1}?"
                }
                if question_type == "multiple_choice":
                    question.update({
                        "options": ["A", "B", "C", "D"],
                        "correct_answer": "A"
                    })
                elif question_type == "true_false":
                    question["correct_answer"] = "True"
                else:
                    question.update({
                        "correct_answer": "Model answer.",
                        "keywords": ["first", "second", "third"]
                    })
                questions.append(question)
        QuestionRepository.save_all(article_id, questions)

    exam = ExamService.get_random_exam()
    assert len(exam["articles"]) == 4
    assert exam["article"].id == exam["articles"][0].id
    assert set(exam["article_ids"]) == set(article_ids)
    assert len(exam["questions"]) == 18
    assert {
        kind: sum(q.question_type == kind for q in exam["questions"])
        for kind in ("multiple_choice", "true_false", "open")
    } == {
        "multiple_choice": 4,
        "true_false": 4,
        "open": 10
    }
    assert all(
        question.correct_answer
        for question in exam["questions"]
        if question.question_type == "open"
    )

    with patch.object(
        exam_service,
        "generate_questions",
        return_value=generated_questions()
    ):
        created_id = ExamService.add_approved_library_article(
            Article(
                id=None,
                title="Another title",
                source="Licensed source",
                content="Licensed article text",
                detected_level="B2",
                level_confidence=0.9,
                subject="Education",
                subject_confidence=0.9,
                word_count=3
            ),
            rights_basis="Written permission",
            permission_reference="permission-ref-001",
            approved_by="reviewer"
        )

    assert created_id is not None
    assert len(QuestionRepository.find_by_article_id(created_id)) == 5


def test_exam_service_does_not_store_library_article_when_question_generation_fails(
        database
):
    with patch.object(exam_service, "generate_questions", return_value=[]):
        created_id = ExamService.add_approved_library_article(
            Article(
                id=None,
                title="Not ready",
                source="Licensed source",
                content="Licensed text",
                detected_level="B1",
                level_confidence=0.8,
                subject="Work",
                subject_confidence=0.9,
                word_count=2
            ),
            rights_basis="Written permission",
            permission_reference="permission-ref-002",
            approved_by="reviewer"
        )

    assert created_id is None
    with closing(database()) as connection:
        assert connection.execute(
            "SELECT COUNT(*) FROM articles"
        ).fetchone()[0] == 0


def test_article_repository_enforces_the_10_article_category_quota(database):
    for index in range(10):
        ArticleRepository.save_approved_exam_article(
            Article(
                id=None,
                title=f"Notice {index}",
                source=f"https://publisher.example/{index}",
                content="Licensed notice text.",
                detected_level="B1",
                level_confidence=0.8,
                subject="Society",
                subject_confidence=0.9,
                word_count=30,
                exam_category="notice"
            ),
            rights_basis="CC BY 4.0",
            permission_reference="https://publisher.example/license",
            approved_by="reviewer",
            exam_category="notice"
        )

    with pytest.raises(ValueError, match="limit of 30"):
        ArticleRepository.save_approved_exam_article(
            Article(
                id=None,
                title="Notice 11",
                source="https://publisher.example/11",
                content="Licensed notice text.",
                detected_level="B1",
                level_confidence=0.8,
                subject="Society",
                subject_confidence=0.9,
                word_count=30,
                exam_category="notice"
            ),
            rights_basis="CC BY 4.0",
            permission_reference="https://publisher.example/license",
            approved_by="reviewer",
            exam_category="notice"
        )


def test_exam_service_handles_missing_article_or_questions(monkeypatch):
    monkeypatch.setattr(
        exam_service.ArticleRepository,
        "get_random_article_for_category",
        staticmethod(lambda category: None)
    )
    assert ExamService.get_random_exam() is None


def test_article_service_rejects_unsupported_level(monkeypatch):
    monkeypatch.setattr(
        article_service,
        "detect_level",
        lambda content: {"level": "A2", "confidence": 0.9}
    )
    with patch.object(article_service, "classify_subject") as classifier:
        result = article_service.ArticleService.process_article(
            "Content"
        )

    assert result["success"] is False
    classifier.assert_not_called()


def test_score_service_grades_and_persists_full_exam(database):
    article_id = ArticleRepository.save_approved_exam_article(Article(
        id=None,
        title="Title",
        source="Source",
        content="Text",
        detected_level="B1",
        level_confidence=0.8,
        subject="Work",
        subject_confidence=0.9,
        word_count=1
    ), rights_basis="CC BY 4.0", permission_reference="https://example.test",
        approved_by="reviewer")
    second_article_id = ArticleRepository.save_approved_exam_article(
        Article(
            id=None,
            title="Second title",
            source="Second source",
            content="Second text",
            detected_level="B1",
            level_confidence=0.8,
            subject="Society",
            subject_confidence=0.9,
            word_count=2
        ),
        rights_basis="CC BY 4.0",
        permission_reference="https://example.test/license",
        approved_by="reviewer"
    )
    QuestionRepository.save_all(article_id, [
        {
            "type": "multiple_choice",
            "question": "Choose",
            "options": ["A", "B", "C", "D"],
            "correct_answer": "A"
        },
        {
            "type": "true_false",
            "question": "True?",
            "correct_answer": "True"
        },
        {
            "type": "open",
            "question": "Why?",
            "keywords": ["traffic", "environment", "emissions"]
        }
    ])
    questions = QuestionRepository.find_by_article_id(article_id)

    result = ScoreService.grade_exam(
        article_id,
        "B1",
        questions,
        {
            "q1": "a",
            "q2": "True",
            "q3": "traffic and emissions"
        },
        article_ids=[article_id, second_article_id]
    )

    assert result["score"] == 100.0
    assert result["correct_answers"] == 3
    assert result["total_questions"] == 3
    assert result["exam_result_id"] is not None
    with closing(database()) as connection:
        assert connection.execute(
            "SELECT COUNT(*) FROM user_answers"
        ).fetchone()[0] == 3
        assert connection.execute("""
            SELECT article_id, article_order
            FROM exam_result_articles
            WHERE exam_result_id = ?
            ORDER BY article_order
        """, (result["exam_result_id"],)).fetchall() == [
            (article_id, 1),
            (second_article_id, 2)
        ]


def test_score_service_keeps_user_article_exam_result_in_memory(database):
    ephemeral_questions = [
        question(None, "true_false", "True"),
        question(None, "true_false", "False")
    ]
    for item in ephemeral_questions:
        item.article_id = None

    result = ScoreService.grade_exam(
        article_id=None,
        article_level="B1",
        questions=ephemeral_questions,
        user_answers={"q1": "True", "q2": "False"}
    )

    assert result["score"] == 100
    assert result["exam_result_id"] is None
    with closing(database()) as connection:
        assert connection.execute(
            "SELECT COUNT(*) FROM exam_results"
        ).fetchone()[0] == 0
        assert connection.execute(
            "SELECT COUNT(*) FROM user_answers"
        ).fetchone()[0] == 0


def test_score_service_rejects_empty_exam():
    with pytest.raises(ValueError, match="no questions"):
        ScoreService.grade_exam(1, "B1", [], {})


def test_open_answer_grader_supports_legacy_and_json_keywords():
    assert ScoreService._grade_open(
        question(1, "open", "", "['traffic', 'emissions']"),
        "traffic and emissions"
    )
    assert ScoreService._grade_open(
        question(1, "open", "", '["traffic", "emissions"]'),
        "traffic and emissions"
    )
    assert not ScoreService._grade_open(
        question(1, "open", "", "invalid"),
        "traffic and emissions"
    )
    assert not ScoreService._grade_open(
        question(1, "open", "", '{"not": "a list"}'),
        "traffic and emissions"
    )
    assert not ScoreService._grade_open(
        question(1, "open", "", None),
        "traffic and emissions"
    )
    assert not ScoreService._grade_question(
        question(1, "unknown", "", None),
        "answer"
    )


def test_ai_feedback_builds_recommendations_and_goals():
    feedback = AIFeedbackService.generate_feedback(
        "B2",
        {
            "score": 50,
            "details": [
                {
                    "question": "Open question",
                    "question_type": "open",
                    "user_answer": "short",
                    "correct_answer": "complete",
                    "is_correct": False
                },
                {
                    "question": "Choice",
                    "question_type": "multiple_choice",
                    "user_answer": "A",
                    "correct_answer": "B",
                    "is_correct": False
                }
            ]
        }
    )

    assert feedback.reading_level == "B2"
    assert len(feedback.weaknesses) == 2
    assert any("written responses" in item for item in feedback.recommendations)
    assert "Review the article" in feedback.next_goal


def test_ai_feedback_recommends_maintenance_after_all_answers_correct():
    feedback = AIFeedbackService.generate_feedback(
        "B1",
        {
            "score": 100,
            "details": [{
                "question": "Question",
                "question_type": "multiple_choice",
                "user_answer": "A",
                "correct_answer": "A",
                "is_correct": True
            }]
        }
    )

    assert feedback.recommendations == [
        "Continue reading B1 articles regularly to maintain your level."
    ]


def test_ai_feedback_adds_true_false_recommendation():
    feedback = AIFeedbackService.generate_feedback(
        "B1",
        {
            "score": 0,
            "details": [{
                "question": "True or false?",
                "question_type": "true_false",
                "user_answer": "True",
                "correct_answer": "False",
                "is_correct": False
            }]
        }
    )

    assert any("distinguishing facts" in item for item in feedback.recommendations)


@pytest.mark.parametrize(
    ("score", "expected"),
    [
        (95, "Excellent"),
        (85, "Very good"),
        (65, "Good effort"),
        (45, "partial"),
        (10, "challenging")
    ]
)
def test_ai_feedback_score_bands(score, expected):
    assert expected in AIFeedbackService._generate_overall_feedback(score)


def test_ai_feedback_goals_for_high_and_middle_scores():
    assert "B2 texts" in AIFeedbackService._generate_next_goal(95, "B1")
    assert "Complete another B2 article" in AIFeedbackService._generate_next_goal(
        75,
        "B2"
    )
