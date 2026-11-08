from ai.level_detector import detect_level
from ai.subject_classifier import classify_subject
from ai.question_generator import generate_questions

import json

from backend.skills.reading.models.question import Question


class ArticleService:

    @staticmethod
    def process_article(content: str):
        if not isinstance(content, str) or not content.strip():
            return {
                "success": False,
                "message": "Please enter the article content."
            }

        level_result = detect_level(
            content
        )

        level = level_result["level"]

        if level is None:
            return {
                "success": False,
                "message": (
                    "Could not determine the article's level. "
                    "Please try again when the AI service is available."
                )
            }

        if level not in [
            "B1",
            "B2",
            "C1"
        ]:

            return {

                "success": False,

                "message":
                (
                    "This article is not suitable "
                    "for YKI practice. "
                    "Please choose a longer and "
                    "more challenging article."
                )
            }

        subject_result = (
            classify_subject(
                content
            )
        )

        if subject_result["subject"] is None:
            return {
                "success": False,
                "message": (
                    "Could not classify the article's subject. "
                    "Please try again when the AI service is available."
                )
            }

        questions = (
            generate_questions(
                content
            )
        )

        if not questions:
            return {
                "success": False,
                "message": (
                    "Could not generate valid exam questions for this article. "
                    "Please try again."
                )
            }

        session_questions = [
            Question(
                id=None,
                article_id=None,
                question_no=index,
                question_type=question["type"],
                question=question["question"],
                option_a=question.get("options", [None] * 4)[0],
                option_b=question.get("options", [None] * 4)[1],
                option_c=question.get("options", [None] * 4)[2],
                option_d=question.get("options", [None] * 4)[3],
                correct_answer=question.get("correct_answer", ""),
                keywords=json.dumps(
                    question.get("keywords", []),
                    ensure_ascii=False
                ),
                explanation=question.get("explanation", "")
            )
            for index, question in enumerate(questions, start=1)
        ]

        return {

            "success": True,

            "article_id": None,

            "level":
                level,

            "subject":
                subject_result[
                    "subject"
                ],

            "questions":
                session_questions
        }