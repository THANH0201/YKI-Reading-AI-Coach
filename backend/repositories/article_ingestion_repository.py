from backend.database.db import get_connection
from backend.ai_neural_networks.reading.models.exam_category import (
    ARTICLE_QUOTA_PER_CATEGORY,
    EXAM_CATEGORY_RULES
)


class ArticleIngestionRepository:

    @staticmethod
    def add_source(
            publisher: str,
            feed_url: str,
            rights_basis: str,
            permission_reference: str,
            approved_by: str,
            exam_category: str = "utiset"
    ) -> int:
        if exam_category not in EXAM_CATEGORY_RULES:
            raise ValueError("Unsupported sample-exam article category.")
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO article_ingestion_sources(
                    publisher,
                    feed_url,
                    rights_basis,
                    permission_reference,
                    approved_by,
                    exam_category
                )
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(feed_url) DO UPDATE SET
                    publisher = excluded.publisher,
                    rights_basis = excluded.rights_basis,
                    permission_reference = excluded.permission_reference,
                    approved_by = excluded.approved_by,
                    exam_category = excluded.exam_category,
                    active = 1
            """, (
                publisher.strip(),
                feed_url.strip(),
                rights_basis.strip(),
                permission_reference.strip(),
                approved_by.strip(),
                exam_category
            ))
            conn.commit()
            cursor.execute(
                "SELECT id FROM article_ingestion_sources WHERE feed_url = ?",
                (feed_url.strip(),)
            )
            row = cursor.fetchone()
            if row is None:
                raise RuntimeError("The ingestion source could not be saved.")
            return row[0]
        finally:
            conn.close()

    @staticmethod
    def find_source(source_id: int) -> dict | None:
        conn = get_connection()
        try:
            row = conn.execute("""
                SELECT
                    id, publisher, feed_url, rights_basis,
                    permission_reference, approved_by, exam_category
                FROM article_ingestion_sources
                WHERE id = ? AND active = 1
            """, (source_id,)).fetchone()
        finally:
            conn.close()

        if row is None:
            return None

        return {
            "id": row[0],
            "publisher": row[1],
            "feed_url": row[2],
            "rights_basis": row[3],
            "permission_reference": row[4],
            "approved_by": row[5],
            "exam_category": row[6]
        }

    @staticmethod
    def list_sources() -> list[dict]:
        conn = get_connection()
        try:
            rows = conn.execute("""
                SELECT id, publisher, feed_url, rights_basis,
                       permission_reference, approved_by, exam_category,
                       last_checked_at
                FROM article_ingestion_sources
                WHERE active = 1
                ORDER BY publisher, id
            """).fetchall()
        finally:
            conn.close()

        return [
            {
                "id": row[0],
                "publisher": row[1],
                "feed_url": row[2],
                "rights_basis": row[3],
                "permission_reference": row[4],
                "approved_by": row[5],
                "exam_category": row[6],
                "last_checked_at": row[7]
            }
            for row in rows
        ]

    @staticmethod
    def has_article_url(article_url: str) -> bool:
        conn = get_connection()
        try:
            row = conn.execute(
                "SELECT 1 FROM articles WHERE source = ? LIMIT 1",
                (article_url,)
            ).fetchone()
        finally:
            conn.close()
        return row is not None

    @staticmethod
    def count_approved_articles(exam_category: str) -> int:
        conn = get_connection()
        try:
            count = conn.execute("""
                SELECT COUNT(*)
                FROM articles
                WHERE reuse_approved = 1 AND exam_category = ?
            """, (exam_category,)).fetchone()[0]
        finally:
            conn.close()
        return count

    @staticmethod
    def remaining_article_capacity(exam_category: str) -> int:
        return max(
            0,
            ARTICLE_QUOTA_PER_CATEGORY
            - ArticleIngestionRepository.count_approved_articles(
                exam_category
            )
        )

    @staticmethod
    def mark_checked(source_id: int) -> None:
        conn = get_connection()
        try:
            conn.execute("""
                UPDATE article_ingestion_sources
                SET last_checked_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (source_id,))
            conn.commit()
        finally:
            conn.close()
