import logging
import xml.etree.ElementTree as ET

from backend.functions.reading.ai.level_detector import detect_level
from backend.functions.reading.ai.subject_classifier import classify_subject
from backend.functions.reading.models.article import Article
from backend.functions.reading.models.exam_category import (
    ARTICLE_QUOTA_PER_CATEGORY,
    EXAM_CATEGORY_RULES,
)

from backend.functions.reading.repositories.article_ingestion_repository import (
    ArticleIngestionRepository,
)
from backend.functions.reading.services.exam_service import ExamService
from backend.functions.reading.tools.rss_feed_tool import (
    fetch_feed,
    parse_feed,
    validate_public_feed_url,
    word_count,
)

logger = logging.getLogger(__name__)


class ArticleIngestionService:
    @staticmethod
    def add_source_and_crawl(
        publisher: str,
        feed_url: str,
        rights_basis: str,
        permission_reference: str,
        approved_by: str,
        rights_confirmed: bool,
        exam_category: str = "utiset",
    ) -> dict:

        required_fields = {
            "publisher": publisher,
            "feed URL": feed_url,
            "license or permission": rights_basis,
            "license/permission reference": permission_reference,
            "approver": approved_by,
        }

        missing = [
            label
            for label, value in required_fields.items()
            if not isinstance(value, str) or not value.strip()
        ]

        if missing:
            raise ValueError("Please provide: " + ", ".join(missing) + ".")

        if rights_confirmed is not True:
            raise ValueError(
                "Confirm that the license permits storing, "
                "adapting, AI processing, and displaying "
                "the full article."
            )

        if exam_category not in EXAM_CATEGORY_RULES:
            raise ValueError("Select one of the supported YKI article types.")

        validate_public_feed_url(feed_url.strip())

        source_id = ArticleIngestionRepository.add_source(
            publisher,
            feed_url,
            rights_basis,
            permission_reference,
            approved_by,
            exam_category=exam_category,
        )

        return ArticleIngestionService.crawl_source(source_id)

    @staticmethod
    def crawl_source(source_id: int) -> dict:

        source = ArticleIngestionRepository.find_source(source_id)

        if source is None:
            raise ValueError("The approved feed source was not found.")

        feed_content = fetch_feed(source["feed_url"])

        try:
            entries = parse_feed(feed_content)

        except ET.ParseError as error:
            raise ValueError("The URL did not return a valid RSS/Atom feed.") from error

        result = {
            "imported": [],
            "skipped": [],
            "failed": [],
        }

        category_rules = EXAM_CATEGORY_RULES[source["exam_category"]]

        category_capacity = ArticleIngestionRepository.remaining_article_capacity(
            source["exam_category"]
        )

        for entry in entries:
            if ArticleIngestionRepository.has_article_url(entry["url"]):
                result["skipped"].append(
                    {"title": entry["title"], "reason": "Already imported."}
                )
                continue

            if category_capacity <= 0:
                result["skipped"].append(
                    {
                        "title": entry["title"],
                        "reason": (
                            f"The "
                            f"{source['exam_category']} "
                            f"pool already has "
                            f"{ARTICLE_QUOTA_PER_CATEGORY} "
                            f"articles."
                        ),
                    }
                )
                continue

            count = word_count(entry["content"])

            if not (
                category_rules["min_words"] <= count <= category_rules["max_words"]
            ):
                result["skipped"].append(
                    {
                        "title": entry["title"],
                        "reason": (
                            f"Feed content has {count} words; "
                            f"accepted range is "
                            f"{category_rules['min_words']}-"
                            f"{category_rules['max_words']}."
                        ),
                    }
                )
                continue

            level_result = detect_level(entry["content"])

            detected_level = level_result.get("level")

            target_level = category_rules["target_level"]

            supported_levels = {
                "A2",
                "B1",
                "B2",
                "C1",
            }

            if detected_level not in supported_levels or (
                target_level is not None and detected_level != target_level
            ):
                result["skipped"].append(
                    {
                        "title": entry["title"],
                        "reason": (
                            f"Could not verify required {target_level} level."
                            if target_level
                            else "Could not verify a supported level."
                        ),
                    }
                )
                continue

            subject_result = classify_subject(entry["content"])

            if subject_result.get("subject") is None:
                result["skipped"].append(
                    {
                        "title": entry["title"],
                        "reason": ("Could not classify article subject."),
                    }
                )
                continue

            article = Article(
                id=None,
                title=entry["title"],
                source=entry["url"],
                content=entry["content"],
                detected_level=detected_level,
                level_confidence=level_result["confidence"],
                subject=subject_result["subject"],
                subject_confidence=subject_result["confidence"],
                word_count=count,
                exam_category=source["exam_category"],
            )

            article_id = ExamService.add_approved_library_article(
                article,
                rights_basis=source["rights_basis"],
                permission_reference=source["permission_reference"],
                approved_by=source["approved_by"],
                exam_category=source["exam_category"],
            )

            if article_id is None:
                result["failed"].append(
                    {
                        "title": entry["title"],
                        "reason": ("Could not generate a valid five-question exam."),
                    }
                )

            else:
                result["imported"].append(
                    {
                        "title": entry["title"],
                        "article_id": article_id,
                        "word_count": count,
                        "level": article.detected_level,
                        "subject": article.subject,
                    }
                )

                category_capacity -= 1

        ArticleIngestionRepository.mark_checked(source_id)

        logger.info(
            ("Feed ingestion complete for source_id=%s: imported=%s skipped=%s"),
            source_id,
            len(result["imported"]),
            len(result["skipped"]),
        )

        return result

    @staticmethod
    def crawl_all_sources():

        results = []

        for source in ArticleIngestionRepository.list_sources():
            try:
                result = ArticleIngestionService.crawl_source(source["id"])

            except (
                ValueError,
                OSError,
            ) as error:
                results.append(
                    {
                        "publisher": source["publisher"],
                        "error": str(error),
                    }
                )

            else:
                results.append(
                    {
                        "publisher": source["publisher"],
                        **result,
                    }
                )

        return results

    @staticmethod
    def list_sources():

        return ArticleIngestionRepository.list_sources()

    @staticmethod
    def remaining_article_capacity(exam_category: str) -> int:

        if exam_category not in EXAM_CATEGORY_RULES:
            raise ValueError("Unsupported sample-exam article category.")

        return ArticleIngestionRepository.remaining_article_capacity(exam_category)
