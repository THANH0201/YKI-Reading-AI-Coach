from backend.database.db import get_connection

class UserAnswerRepository:

    @staticmethod
    def save_all(answers):

        conn = get_connection()

        cursor = conn.cursor()

        for answer in answers:

            cursor.execute("""
                INSERT INTO user_answers(

                    exam_result_id,
                    question_id,
                    selected_answer,
                    is_correct

                )
                VALUES(?,?,?,?)
            """, (

                answer.exam_result_id,
                answer.question_id,
                answer.selected_answer,
                answer.is_correct

            ))

        conn.commit()

        conn.close()