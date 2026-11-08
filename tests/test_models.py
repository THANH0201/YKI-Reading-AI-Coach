from backend.ai_neural_networks.reading.models.article import Article
from backend.ai_neural_networks.reading.models.exam_result import ExamResult
from backend.ai_neural_networks.reading.models.feedback import Feedback
from backend.ai_neural_networks.reading.models.question import Question
from backend.ai_neural_networks.reading.models.user_answer import UserAnswer


def test_domain_models_accept_workflow_data():
    article = Article(
        id=1,
        title="Finnish article",
        source="News",
        content="Text",
        detected_level="B1",
        level_confidence=0.8,
        subject="Society",
        subject_confidence=0.9,
        word_count=1
    )
    question = Question(
        id=2,
        article_id=1,
        question_no=1,
        question_type="true_false",
        question="Is it true?",
        option_a=None,
        option_b=None,
        option_c=None,
        option_d=None,
        correct_answer="True",
        keywords="[]",
        explanation="Text says so."
    )
    result = ExamResult(
        id=3,
        article_id=1,
        score=100.0,
        correct_answers=1,
        total_questions=1
    )
    answer = UserAnswer(
        id=4,
        exam_result_id=3,
        question_id=2,
        selected_answer="True",
        is_correct=True
    )
    feedback = Feedback(
        overall_feedback="Great.",
        reading_level="B1",
        strengths=[],
        weaknesses=[],
        recommendations=["Keep reading."],
        next_goal="Try another article."
    )

    assert article.level_confidence == 0.8
    assert question.article_id == article.id
    assert result.score == 100.0
    assert answer.is_correct
    assert feedback.reading_level == "B1"
