from backend.functions.reading.models.article import Article
from backend.functions.reading.models.exam_category import (
    ARTICLE_QUOTA_PER_CATEGORY,
    EXAM_CATEGORY_RULES,
)

from backend.database.db import get_connection


class ArticleRepository:
    @staticmethod
    def validate_reuse_approval(
        rights_basis: str, permission_reference: str, approved_by: str
    ) -> None:
        required_values = {
            "rights_basis": rights_basis,
            "permission_reference": permission_reference,
            "approved_by": approved_by,
        }
        missing_values = [
            field
            for field, value in required_values.items()
            if not isinstance(value, str) or not value.strip()
        ]
        if missing_values:
            raise ValueError(
                "Approved exam articles require non-empty "
                + ", ".join(missing_values)
                + "."
            )

    @staticmethod
    def save_approved_exam_article(
        article: Article,
        rights_basis: str,
        permission_reference: str,
        approved_by: str,
        exam_category: str | None = None,
    ):
        ArticleRepository.validate_reuse_approval(
            rights_basis, permission_reference, approved_by
        )
        category = exam_category or article.exam_category
        if category is not None and category not in EXAM_CATEGORY_RULES:
            raise ValueError("Unsupported sample-exam article category.")

        conn = get_connection()
        try:
            cursor = conn.cursor()
            if category is not None:
                cursor.execute("BEGIN IMMEDIATE")
                category_count = cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM articles
                    WHERE reuse_approved = 1 AND exam_category = ?
                """,
                    (category,),
                ).fetchone()[0]
                if category_count >= ARTICLE_QUOTA_PER_CATEGORY:
                    raise ValueError(
                        f"The {category} article pool already contains "
                        "its limit of 30 approved articles."
                    )
            cursor.execute(
                """
                INSERT INTO articles(
                    title,
                    source,
                    content,
                    detected_level,
                    level_confidence,
                    subject,
                    subject_confidence,
                    word_count,
                    reuse_approved,
                    rights_basis,
                    permission_reference,
                    reuse_approved_by,
                    reuse_approved_at,
                    exam_category
                )
                VALUES(?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?, ?, CURRENT_TIMESTAMP, ?)
            """,
                (
                    article.title,
                    article.source,
                    article.content,
                    article.detected_level,
                    article.level_confidence,
                    article.subject,
                    article.subject_confidence,
                    article.word_count,
                    rights_basis.strip(),
                    permission_reference.strip(),
                    approved_by.strip(),
                    category,
                ),
            )
            conn.commit()
            article_id = cursor.lastrowid
        finally:
            conn.close()

        return article_id

    @staticmethod
    def get_random_article_for_category(exam_category: str):
        distribution = EXAM_CATEGORY_RULES[exam_category]["question_distribution"]
        total_questions = sum(distribution.values())
        conn = get_connection()

        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT
                    id,
                    title,
                    source,
                    content,
                    detected_level,
                    level_confidence,
                    subject,
                    subject_confidence,
                    word_count,
                    created_at
                FROM articles AS article
                WHERE reuse_approved = 1
                  AND exam_category = ?
                  AND (
                    ? IS NULL OR detected_level = ?
                  )
                  AND (
                    SELECT COUNT(*)
                    FROM questions
                    WHERE questions.article_id = article.id
                  ) = ?
                  AND (
                    SELECT COUNT(*)
                    FROM questions
                    WHERE questions.article_id = article.id
                      AND questions.question_type = ?
                  ) = ?
                ORDER BY RANDOM()
                LIMIT 1
            """,
                (
                    exam_category,
                    EXAM_CATEGORY_RULES[exam_category]["target_level"],
                    EXAM_CATEGORY_RULES[exam_category]["target_level"],
                    total_questions,
                    next(iter(distribution)),
                    next(iter(distribution.values())),
                ),
            )
            row = cursor.fetchone()
        finally:
            conn.close()

        if row is None:
            return None

        return Article(
            id=row[0],
            title=row[1],
            source=row[2],
            content=row[3],
            detected_level=row[4],
            level_confidence=row[5],
            subject=row[6],
            subject_confidence=row[7],
            word_count=row[8],
            created_at=row[9],
            exam_category=exam_category,
        )

    @staticmethod
    def get_random_article():
        conn = get_connection()

        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT
                    id,
                    title,
                    source,
                    content,
                    detected_level,
                    level_confidence,
                    subject,
                    subject_confidence,
                    word_count,
                    created_at
                FROM articles
                WHERE reuse_approved = 1
                  AND EXISTS (
                    SELECT 1
                    FROM questions
                    WHERE questions.article_id = articles.id
                )
                ORDER BY RANDOM()
                LIMIT 1
            """)
            row = cursor.fetchone()
        finally:
            conn.close()

        if row is None:
            return None

        return Article(
            id=row[0],
            title=row[1],
            source=row[2],
            content=row[3],
            detected_level=row[4],
            level_confidence=row[5],
            subject=row[6],
            subject_confidence=row[7],
            word_count=row[8],
            created_at=row[9],
        )
