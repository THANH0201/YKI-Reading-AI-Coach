import ast
import json

from models.exam_result import ExamResult
from models.user_answer import UserAnswer

from repositories.exam_result_repository import (
    ExamResultRepository
)

from repositories.user_answer_repository import (
    UserAnswerRepository
)

from services.ai_feedback_service import (
    AIFeedbackService
)


class ScoreService:

    @staticmethod
    def grade_exam(
            article_id,
            article_level,
            questions,
            user_answers,
            article_ids=None):

        total_questions = len(questions)
        if total_questions == 0:
            raise ValueError("Cannot grade an exam with no questions.")

        correct_count = 0

        details = []

        for index, question in enumerate(
                questions,
                start=1
        ):

            user_answer = user_answers.get(
                f"q{index}",
                ""
            )

            is_correct = (
                ScoreService._grade_question(
                    question,
                    user_answer
                )
            )

            if is_correct:
                correct_count += 1

            details.append({
                "question_id":
                    question.id,

                "question":
                    question.question,

                "question_type":
                    question.question_type,

                "user_answer":
                    user_answer,

                "correct_answer":
                    question.correct_answer,

                "is_correct":
                    is_correct
            })

        score = (
            round(
                correct_count * 100 /
                total_questions,
                2
            )
            if total_questions > 0
            else 0
        )

        exam_result_id = None
        can_persist_result = (
            article_id is not None
            and all(question.id is not None for question in questions)
        )
        if can_persist_result:
            exam_result = ExamResult(
                id=None,
                article_id=article_id,
                score=score,
                correct_answers=correct_count,
                total_questions=total_questions
            )

            exam_result_id = ExamResultRepository.save(
                exam_result,
                article_ids=article_ids
            )
            saved_answers = [
                UserAnswer(
                    id=None,
                    exam_result_id=exam_result_id,
                    question_id=question.id,
                    selected_answer=str(
                        user_answers.get(f"q{index}", "")
                    ),
                    is_correct=details[index - 1]["is_correct"]
                )
                for index, question in enumerate(questions, start=1)
            ]
            UserAnswerRepository.save_all(saved_answers)

        feedback = (
            AIFeedbackService.generate_feedback(
                article_level=article_level,
                score_result={
                    "score": score,
                    "details": details
                }
            )
        )

        return {

            "exam_result_id":
                exam_result_id,

            "score":
                score,

            "correct_answers":
                correct_count,

            "total_questions":
                total_questions,

            "details":
                details,

            "feedback":
                feedback
        }

    @staticmethod
    def _grade_question(
            question,
            user_answer):

        graders = {

            "multiple_choice":
                ScoreService._grade_choice,

            "true_false":
                ScoreService._grade_choice,

            "open":
                ScoreService._grade_open
        }

        grader = graders.get(
            question.question_type
        )

        if grader is None:
            return False

        return grader(
            question,
            user_answer
        )

    @staticmethod
    def _grade_choice(
            question,
            user_answer):

        return (
            str(user_answer).strip().lower()
            ==
            str(
                question.correct_answer
            ).strip().lower()
        )

    @staticmethod
    def _grade_open(
            question,
            user_answer):

        if not question.keywords:
            return False

        try:
            keywords = json.loads(
                question.keywords
            )
        except (json.JSONDecodeError, TypeError):
            try:
                keywords = ast.literal_eval(question.keywords)
            except (SyntaxError, ValueError, TypeError):
                return False

        if (
            not isinstance(keywords, list)
            or not keywords
            or not all(isinstance(keyword, str) for keyword in keywords)
        ):
            return False

        answer = str(
            user_answer
        ).lower()

        matched = sum(
            1
            for keyword in keywords
            if keyword.lower() in answer
        )

        required_matches = max(
            1,
            round(
                len(keywords) * 0.6
            )
        )

        return (
            matched >= required_matches
        )