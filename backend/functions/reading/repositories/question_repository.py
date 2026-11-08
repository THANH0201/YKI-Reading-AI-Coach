import json

from backend.functions.reading.models.exam_category import EXAM_CATEGORY_RULES
from backend.functions.reading.models.question import Question

from backend.database.db import get_connection


class QuestionRepository:
    @staticmethod
    def save_all(article_id, questions):

        conn = get_connection()

        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT reuse_approved, exam_category
                FROM articles
                WHERE id = ?
            """,
                (article_id,),
            )
            article = cursor.fetchone()
            if article is None or article[0] != 1:
                raise ValueError(
                    "Questions can only be saved for an approved exam library article."
                )
            category = article[1]
            if category in EXAM_CATEGORY_RULES:
                expected_distribution = EXAM_CATEGORY_RULES[category][
                    "question_distribution"
                ]
                actual_distribution: dict[str, int] = {}
                for question in questions:
                    question_type = question.get("type")
                    if (
                        not isinstance(question_type, str)
                        or question_type not in expected_distribution
                    ):
                        raise ValueError(f"Unsupported question type for {category}.")
                    actual_distribution[question_type] = (
                        actual_distribution.get(question_type, 0) + 1
                    )
                if actual_distribution != expected_distribution:
                    raise ValueError(
                        f"Questions for {category} articles must follow "
                        f"the required distribution {expected_distribution}."
                    )
                if category in {"utiset", "selkouutiset"} and any(
                    not isinstance(question.get("correct_answer"), str)
                    or not question["correct_answer"].strip()
                    for question in questions
                ):
                    raise ValueError(
                        "Open questions in long-form sample exams require "
                        "a saved model answer."
                    )

            for index, q in enumerate(questions, start=1):
                options = q.get("options", [])

                cursor.execute(
                    """
            INSERT INTO questions(

                article_id,
                question_no,

                question_type,
                question,

                option_a,
                option_b,
                option_c,
                option_d,

                correct_answer,

                keywords,

                explanation

            )
            VALUES(
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
                """,
                    (
                        article_id,
                        index,
                        q["type"],
                        q["question"],
                        options[0] if len(options) > 0 else None,
                        options[1] if len(options) > 1 else None,
                        options[2] if len(options) > 2 else None,
                        options[3] if len(options) > 3 else None,
                        q.get("correct_answer", ""),
                        json.dumps(q.get("keywords", []), ensure_ascii=False),
                        q.get("explanation", ""),
                    ),
                )

            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def find_by_article_id(article_id):
        conn = get_connection()

        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT
                    id,
                    article_id,
                    question_no,
                    question_type,
                    question,
                    option_a,
                    option_b,
                    option_c,
                    option_d,
                    correct_answer,
                    keywords,
                    explanation
                FROM questions
                WHERE article_id = ?
                ORDER BY question_no
            """,
                (article_id,),
            )
            rows = cursor.fetchall()
        finally:
            conn.close()

        return [
            Question(
                id=row[0],
                article_id=row[1],
                question_no=row[2],
                question_type=row[3],
                question=row[4],
                option_a=row[5],
                option_b=row[6],
                option_c=row[7],
                option_d=row[8],
                correct_answer=row[9],
                keywords=row[10],
                explanation=row[11],
            )
            for row in rows
        ]
