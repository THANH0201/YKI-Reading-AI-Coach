from backend.functions.reading.ai.question_generator import generate_questions
from backend.functions.reading.models.exam_category import EXAM_CATEGORY_RULES

from backend.functions.reading.repositories.article_repository import ArticleRepository
from backend.functions.reading.repositories.question_repository import (
    QuestionRepository,
)


class ExamService:
    @staticmethod
    def get_random_exam():
        categories = ("notice", "email", "utiset", "selkouutiset")
        articles = []
        questions = []
        for category in categories:
            article = ArticleRepository.get_random_article_for_category(category)
            if article is None:
                return None
            articles.append(article)
            questions.extend(QuestionRepository.find_by_article_id(article.id))
        return {
            "article": articles[0],
            "articles": articles,
            "article_ids": [article.id for article in articles],
            "questions": questions,
        }

    @staticmethod
    def add_approved_library_article(
        article,
        rights_basis: str,
        permission_reference: str,
        approved_by: str,
        exam_category: str | None = None,
    ) -> int | None:
        ArticleRepository.validate_reuse_approval(
            rights_basis, permission_reference, approved_by
        )
        category = exam_category or article.exam_category
        distribution = (
            EXAM_CATEGORY_RULES[category]["question_distribution"]
            if category in EXAM_CATEGORY_RULES
            else None
        )
        questions = generate_questions(
            article.content,
            question_distribution=distribution,
            require_open_answer=category in {"utiset", "selkouutiset"},
        )
        if not questions:
            return None

        article.exam_category = category
        article_id = ArticleRepository.save_approved_exam_article(
            article,
            rights_basis=rights_basis,
            permission_reference=permission_reference,
            approved_by=approved_by,
            exam_category=category,
        )
        QuestionRepository.save_all(article_id, questions)
        return article_id
