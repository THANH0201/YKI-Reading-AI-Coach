from backend.database.db import get_connection


class ExamResultRepository:
    @staticmethod
    def save(result, article_ids=None):

        conn = get_connection()

        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO exam_results(
                    article_id,
                    score,
                    correct_answers,
                    total_questions
                )
                VALUES(?,?,?,?)
            """,
                (
                    result.article_id,
                    result.score,
                    result.correct_answers,
                    result.total_questions,
                ),
            )
            exam_result_id = cursor.lastrowid

            for article_order, article_id in enumerate(
                article_ids or [result.article_id], start=1
            ):
                cursor.execute(
                    """
                    INSERT INTO exam_result_articles(
                        exam_result_id,
                        article_id,
                        article_order
                    )
                    VALUES (?, ?, ?)
                """,
                    (exam_result_id, article_id, article_order),
                )
            conn.commit()
        finally:
            conn.close()

        return exam_result_id
