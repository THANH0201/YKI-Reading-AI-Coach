from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from backend.ai_neural_networks.reading.models.article import Article
from backend.ai_neural_networks.reading.models.feedback import Feedback
from backend.ai_neural_networks.reading.models.question import Question
from backend.ai_neural_networks.reading.services.article_service import ArticleService
from backend.ai_neural_networks.reading.services.exam_service import ExamService
from backend.ai_neural_networks.reading.services.score_service import ScoreService
from backend.ai_neural_networks.reading.services.tutor_service import TutorService
from streamlit.testing.v1 import AppTest


def test_app_renders_home_without_showing_exam_timer(monkeypatch):
    from backend.database import init_db

    calls = []
    monkeypatch.setattr(init_db, "init_db", lambda: calls.append("initialized"))
    app_path = Path(__file__).resolve().parents[1] / "app.py"
    app = AppTest.from_file(app_path)
    app.run()
    app.run()

    assert not app.exception
    assert calls == ["initialized"]
    assert any(
        button.label == "📚 Example Reading Exam"
        for button in app.button
    )
    assert all(
        any(button.label == label for button in app.button)
        for label in ("📖 Reading", "🎧 Listening", "🗣 Speaking", "✍️ Writing")
    )
    assert not any(metric.label == "⏱ Time Remaining" for metric in app.metric)


def test_start_exam_shows_article_questions_timer_and_tutor(monkeypatch):
    from backend.database import init_db

    monkeypatch.setattr(init_db, "init_db", lambda: None)
    app_path = Path(__file__).resolve().parents[1] / "app.py"
    app = AppTest.from_file(app_path)
    app.session_state["article_id"] = 1
    app.session_state["level"] = "B1"
    app.session_state["subject"] = "Work"
    app.session_state["questions"] = [
        Question(
            id=1,
            article_id=1,
            question_no=1,
            question_type="true_false",
            question="Is this statement true?",
            option_a=None,
            option_b=None,
            option_c=None,
            option_d=None,
            correct_answer="True",
            keywords=None,
            explanation=None
        ),
        Question(
            id=2,
            article_id=1,
            question_no=2,
            question_type="multiple_choice",
            question="Choose the correct option.",
            option_a="A",
            option_b="B",
            option_c="C",
            option_d="D",
            correct_answer="A",
            keywords=None,
            explanation=None
        ),
        Question(
            id=3,
            article_id=1,
            question_no=3,
            question_type="open",
            question="Explain your answer.",
            option_a=None,
            option_b=None,
            option_c=None,
            option_d=None,
            correct_answer="",
            keywords='["one"]',
            explanation=None
        )
    ]
    app.run()
    next(button for button in app.button if button.label == "🚀").click().run()

    assert not app.exception
    assert any(metric.label == "⏱ Time Remaining" for metric in app.metric)
    assert any(
        metric.value == "30:00"
        for metric in app.metric
        if metric.label == "⏱ Time Remaining"
    )
    assert any(subheader.value == "Questions" for subheader in app.subheader)
    assert any("AI Tutor" in header.value for header in app.subheader)
    assert any(field.label == "Article Content" for field in app.text_area)
    assert not any(
        field.label in {"Article Title", "Source"}
        for field in app.text_input
    )
    assert len([
        field for field in app.radio
        if field.label == "Select one answer"
    ]) == 2
    assert all(
        field.value is None
        for field in app.radio
        if field.label == "Select one answer"
    )
    assert any(field.label == "Your Answer" for field in app.text_input)
    assert any(button.label == "🏠 Home" for button in app.button)


def test_home_check_level_success_then_start_exam(monkeypatch):
    from backend.database import init_db

    monkeypatch.setattr(init_db, "init_db", lambda: None)
    monkeypatch.setattr(
        ArticleService,
        "process_article",
        staticmethod(lambda content: {
            "success": True,
            "article_id": 1,
            "level": "B1",
            "subject": "Work",
            "questions": [
                Question(
                    id=1,
                    article_id=1,
                    question_no=1,
                    question_type="true_false",
                    question="Is this true?",
                    option_a=None,
                    option_b=None,
                    option_c=None,
                    option_d=None,
                    correct_answer="True",
                    keywords=None,
                    explanation=None
                )
            ]
        })
    )
    app_path = Path(__file__).resolve().parents[1] / "app.py"
    app = AppTest.from_file(app_path).run()
    app.text_area[0].set_value("Finnish text")
    next(
        button for button in app.button if button.label == "Analyze Reading"
    ).click().run()

    assert not app.exception
    assert any(
        "Level: B1" in caption.value
        for caption in app.caption
    )
    next(button for button in app.button if button.label == "🚀").click().run()
    assert any(metric.label == "⏱ Time Remaining" for metric in app.metric)
    assert any(subheader.value == "Questions" for subheader in app.subheader)


def test_home_check_level_failure_clears_old_exam(monkeypatch):
    from backend.database import init_db

    monkeypatch.setattr(init_db, "init_db", lambda: None)
    monkeypatch.setattr(
        ArticleService,
        "process_article",
        staticmethod(lambda content: {
            "success": False,
            "message": "Could not generate valid questions."
        })
    )
    app_path = Path(__file__).resolve().parents[1] / "app.py"
    app = AppTest.from_file(app_path)
    app.session_state["exam_active"] = True
    app.session_state["level"] = "B1"
    app.session_state["questions"] = [
        Question(
            id=1,
            article_id=1,
            question_no=1,
            question_type="true_false",
            question="Old question?",
            option_a=None,
            option_b=None,
            option_c=None,
            option_d=None,
            correct_answer="True",
            keywords=None,
            explanation=None
        )
    ]
    app.session_state["q1"] = "True"
    app.run()
    next(
        button for button in app.button if button.label == "Analyze Reading"
    ).click().run()

    assert not app.exception
    assert any(
        warning.value == "Could not generate valid questions."
        for warning in app.warning
    )
    assert not any(metric.label == "⏱ Time Remaining" for metric in app.metric)


def test_example_exam_button_loads_article_and_questions(monkeypatch):
    from backend.database import init_db

    monkeypatch.setattr(init_db, "init_db", lambda: None)
    monkeypatch.setattr(
        ExamService,
        "get_random_exam",
        staticmethod(lambda: {
            "article": Article(
                id=7,
                title="Sample",
                source="News",
                content="Article text",
                detected_level="B1",
                level_confidence=0.8,
                subject="Society",
                subject_confidence=0.9,
                word_count=2
            ),
            "questions": [
                Question(
                    id=1,
                    article_id=7,
                    question_no=1,
                    question_type="true_false",
                    question="Is this true?",
                    option_a=None,
                    option_b=None,
                    option_c=None,
                    option_d=None,
                    correct_answer="True",
                    keywords=None,
                    explanation=None
                )
            ]
        })
    )
    app_path = Path(__file__).resolve().parents[1] / "app.py"
    app = AppTest.from_file(app_path).run()
    next(
        button for button in app.button
        if button.label == "📚 Example Reading Exam"
    ).click().run()

    assert not app.exception
    assert any(metric.label == "⏱ Time Remaining" for metric in app.metric)
    assert any(
        metric.value == "30:00"
        for metric in app.metric
        if metric.label == "⏱ Time Remaining"
    )
    assert not any(
        field.label in {"Article Title", "Source"}
        for field in app.text_input
    )
    assert not any(field.label == "Article Content" for field in app.text_area)
    assert not any(button.label == "Analyze Reading" for button in app.button)

    next(button for button in app.button if button.label == "🏠 Home").click().run()

    assert not app.session_state.get("exam_active", False)
    assert "exam_articles" not in app.session_state
    assert "questions" not in app.session_state
    assert any(field.label == "Article Content" for field in app.text_area)
    assert not any(button.label == "🏠 Home" for button in app.button)


def test_example_exam_reports_when_no_exam_is_available(monkeypatch):
    from backend.database import init_db

    monkeypatch.setattr(init_db, "init_db", lambda: None)
    monkeypatch.setattr(
        ExamService,
        "get_random_exam",
        staticmethod(lambda: None)
    )
    app_path = Path(__file__).resolve().parents[1] / "app.py"
    app = AppTest.from_file(app_path).run()
    next(
        button for button in app.button
        if button.label == "📚 Example Reading Exam"
    ).click().run()

    assert not app.exception
    assert any(
        warning.value == "No example exam is available."
        for warning in app.warning
    )


def test_writing_section_analyzes_and_displays_feedback(monkeypatch):
    from backend.database import init_db

    analysis = {
        "estimated_level": "B2",
        "assessment": "Your ideas are clear.",
        "strengths": ["Good vocabulary."],
        "corrections": [{
            "original": "Minä menee",
            "corrected": "Minä menen",
            "explanation": "Verb form."
        }],
        "sentence_suggestions": [{
            "original": "Tämä on vaikeaa.",
            "suggestion": "Vaikka tämä on vaikeaa, jatkan.",
            "explanation": "Use a linking clause."
        }],
        "revised_text": "Vaikka tämä on vaikeaa, jatkan."
    }
    monkeypatch.setattr(init_db, "init_db", lambda: None)
    with patch(
        "views.home_page.analyze_writing",
        return_value={"success": True, "analysis": analysis}
    ) as analyze:
        app_path = Path(__file__).resolve().parents[1] / "app.py"
        app = AppTest.from_file(app_path).run()
        next(button for button in app.button if button.label == "✍️ Writing").click().run()
        app.text_area[0].set_value("Minä menee kouluun.")
        next(
            button for button in app.button if button.label == "Analyze Writing"
        ).click().run()

    assert not app.exception
    analyze.assert_called_once_with("Minä menee kouluun.")
    assert any(header.value == "Estimated level: B2" for header in app.subheader)
    assert any("Your ideas are clear." in text.value for text in app.markdown)


def test_listening_and_speaking_sections_are_explicit_placeholders(monkeypatch):
    from backend.database import init_db

    monkeypatch.setattr(init_db, "init_db", lambda: None)
    app_path = Path(__file__).resolve().parents[1] / "app.py"
    app = AppTest.from_file(app_path).run()

    next(
        button for button in app.button if button.label == "🎧 Listening"
    ).click().run()
    assert not app.exception
    assert any(header.value == "Listening Practice" for header in app.title)
    assert any("not available yet" in item.value for item in app.info)

    next(
        button for button in app.button if button.label == "🗣 Speaking"
    ).click().run()
    assert not app.exception
    assert any(header.value == "Speaking Practice" for header in app.title)
    assert any("not available yet" in item.value for item in app.info)


def test_exam_submission_renders_saved_score_and_feedback(monkeypatch):
    from backend.database import init_db

    monkeypatch.setattr(init_db, "init_db", lambda: None)
    app_path = Path(__file__).resolve().parents[1] / "app.py"
    app = AppTest.from_file(app_path)
    app.session_state["exam_active"] = True
    app.session_state["article_id"] = 1
    app.session_state["level"] = "B1"
    app.session_state["subject"] = "Work"
    app.session_state["questions"] = [
        Question(
            id=1,
            article_id=1,
            question_no=1,
            question_type="true_false",
            question="Is this statement true?",
            option_a=None,
            option_b=None,
            option_c=None,
            option_d=None,
            correct_answer="True",
            keywords=None,
            explanation=None
        )
    ]
    feedback = Feedback(
        overall_feedback="Good work.",
        reading_level="B1",
        strengths=[{"question": "Q1", "type": "true_false"}],
        weaknesses=[{
            "question": "Q2",
            "type": "open",
            "your_answer": "",
            "correct_answer": "answer"
        }],
        recommendations=["Keep practicing."],
        next_goal="Try another article."
    )
    result = {
        "score": 100.0,
        "correct_answers": 1,
        "total_questions": 1,
        "details": [
            {
                "is_correct": True,
                "user_answer": "True",
                "correct_answer": "True"
            },
            {
                "is_correct": False,
                "user_answer": "False",
                "correct_answer": "True"
            }
        ],
        "feedback": feedback
    }

    with patch.object(ScoreService, "grade_exam", return_value=result):
        app.run()
        next(button for button in app.button if button.label == "Submit Exam").click().run()

    assert not app.exception
    assert any(header.value == "Exam Result" for header in app.subheader)
    assert any("Score: 100.0%" in message.value for message in app.success)
    assert any(
        message.value
        == "Chat with the AI Tutor to gain a deeper understanding of this article."
        for message in app.info
    )
    assert any(
        message.value == "Question Review"
        for message in app.subheader
    )


def test_timer_expiry_auto_submits_answers_only_once(monkeypatch):
    from frontend.pages import exam_page

    state = {
        "article_id": 1,
        "level": "B1",
        "questions": [
            Question(
                id=1,
                article_id=1,
                question_no=1,
                question_type="true_false",
                question="Is this true?",
                option_a=None,
                option_b=None,
                option_c=None,
                option_d=None,
                correct_answer="True",
                keywords=None,
                explanation=None
            )
        ],
        "q1": "True"
    }
    monkeypatch.setattr(exam_page, "st", SimpleNamespace(session_state=state))

    with patch.object(ScoreService, "grade_exam", return_value={"score": 100}) as grade:
        exam_page._submit_exam(auto_submitted=True)
        exam_page._submit_exam(auto_submitted=True)

    grade.assert_called_once_with(
        article_id=1,
        article_ids=None,
        article_level="B1",
        questions=state["questions"],
        user_answers={"q1": "True"}
    )
    assert state["exam_auto_submitted"] is True
    assert state["exam_active"] is False


def test_tutor_send_displays_answer(monkeypatch):
    from backend.database import init_db

    tutor_calls = []
    monkeypatch.setattr(init_db, "init_db", lambda: None)
    monkeypatch.setattr(
        TutorService,
        "answer",
        staticmethod(
            lambda question, content, **kwargs: (
                tutor_calls.append((question, content, kwargs))
                or {
                    "success": True,
                    "answer": "Tutor response"
                }
            )
        )
    )
    app_path = Path(__file__).resolve().parents[1] / "app.py"
    app = AppTest.from_file(app_path)
    app.session_state["exam_active"] = True
    app.session_state["questions"] = []
    app.session_state["content"] = ""
    app.run()
    next(field for field in app.text_input if field.key == "tutor_question").set_value(
        "What does this mean?"
    ).run()
    next(
        button for button in app.button if button.key == "send_tutor_question"
    ).click().run()

    assert not app.exception
    assert next(
        field for field in app.text_input if field.key == "tutor_question"
    ).value == ""
    assert any(message.value == "Tutor response" for message in app.info)
    assert tutor_calls == [(
        "What does this mean?",
        "",
        {"article_id": None, "subject": None}
    )]


def test_tutor_failure_and_empty_exam_are_shown_in_ui(monkeypatch):
    from backend.database import init_db

    monkeypatch.setattr(init_db, "init_db", lambda: None)
    monkeypatch.setattr(
        TutorService,
        "answer",
        staticmethod(lambda question, content, **kwargs: {
            "success": False,
            "message": "Tutor unavailable."
        })
    )
    app_path = Path(__file__).resolve().parents[1] / "app.py"
    app = AppTest.from_file(app_path)
    app.session_state["exam_active"] = True
    app.session_state["questions"] = []
    app.session_state["content"] = "Article context"
    app.run()
    next(field for field in app.text_input if field.key == "tutor_question").set_value(
        "Question"
    ).run()
    next(
        button for button in app.button if button.key == "send_tutor_question"
    ).click().run()

    assert not app.exception
    assert any(warning.value == "No questions available." for warning in app.warning)
    assert any(warning.value == "Tutor unavailable." for warning in app.warning)


def test_exam_page_warns_on_unsupported_question_type(monkeypatch):
    from backend.database import init_db

    monkeypatch.setattr(init_db, "init_db", lambda: None)
    app_path = Path(__file__).resolve().parents[1] / "app.py"
    app = AppTest.from_file(app_path)
    app.session_state["exam_active"] = True
    app.session_state["questions"] = [
        Question(
            id=1,
            article_id=1,
            question_no=1,
            question_type="unsupported",
            question="Unknown type?",
            option_a=None,
            option_b=None,
            option_c=None,
            option_d=None,
            correct_answer="",
            keywords=None,
            explanation=None
        )
    ]
    app.run()

    assert not app.exception
    assert any(
        "unsupported question type" in warning.value.lower()
        for warning in app.warning
    )
