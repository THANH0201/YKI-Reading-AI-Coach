from backend.skills.reading.models.feedback import Feedback


class AIFeedbackService:

    @staticmethod
    def generate_feedback(
            article_level,
            score_result):

        score = score_result["score"]

        details = score_result["details"]

        strengths = []
        weaknesses = []

        question_type_stats = {

            "multiple_choice": {
                "correct": 0,
                "wrong": 0
            },

            "true_false": {
                "correct": 0,
                "wrong": 0
            },

            "open": {
                "correct": 0,
                "wrong": 0
            }
        }

        for detail in details:

            question_type = detail[
                "question_type"
            ]

            if detail["is_correct"]:

                strengths.append({
                    "question":
                        detail["question"],

                    "type":
                        question_type
                })

                question_type_stats[
                    question_type
                ]["correct"] += 1

            else:

                weaknesses.append({

                    "question":
                        detail["question"],

                    "type":
                        question_type,

                    "your_answer":
                        detail["user_answer"],

                    "correct_answer":
                        detail[
                            "correct_answer"
                        ]

                })

                question_type_stats[
                    question_type
                ]["wrong"] += 1

        overall_feedback = (
            AIFeedbackService
            ._generate_overall_feedback(
                score
            )
        )

        recommendations = (
            AIFeedbackService
            ._generate_recommendations(
                question_type_stats
            )
        )

        next_goal = (
            AIFeedbackService
            ._generate_next_goal(
                score,
                article_level
            )
        )

        return Feedback(

            overall_feedback=
                overall_feedback,

            reading_level=
                article_level,

            strengths=
                strengths,

            weaknesses=
                weaknesses,

            recommendations=
                recommendations,

            next_goal=
                next_goal
        )

    @staticmethod
    def _generate_overall_feedback(
            score):

        if score >= 90:

            return (
                "Excellent work. "
                "You demonstrate strong YKI B1 "
                "reading comprehension."
            )

        if score >= 80:

            return (
                "Very good performance. "
                "You understand most details "
                "and main ideas correctly."
            )

        if score >= 60:

            return (
                "Good effort. "
                "Your comprehension is generally "
                "correct but some skills need "
                "more practice."
            )

        if score >= 40:

            return (
                "Your understanding is partial. "
                "Focus on finding key details "
                "and understanding vocabulary."
            )

        return (
            "This text was challenging. "
            "Continue practicing easier texts "
            "before attempting more difficult "
            "ones."
        )

    @staticmethod
    def _generate_recommendations(
            stats):

        recommendations = []

        if stats["multiple_choice"][
            "wrong"
        ] > 0:

            recommendations.append(
                "Practice identifying main ideas "
                "and key details in articles."
            )

        if stats["true_false"][
            "wrong"
        ] > 0:

            recommendations.append(
                "Focus on distinguishing facts "
                "from misleading information."
            )

        if stats["open"][
            "wrong"
        ] > 0:

            recommendations.append(
                "Improve keyword extraction and "
                "written responses."
            )

        if not recommendations:

            recommendations.append(
                "Continue reading B1 articles "
                "regularly to maintain your level."
            )

        return recommendations

    @staticmethod
    def _generate_next_goal(
            score,
            article_level):

        if score >= 90:

            return (
                f"Try a more challenging "
                f"{article_level} article "
                f"or begin practicing B2 texts."
            )

        if score >= 70:

            return (
                f"Complete another "
                f"{article_level} article "
                f"to reinforce your skills."
            )

        return (
            "Review the article, learn new "
            "vocabulary and retake a similar "
            "exercise."
        )