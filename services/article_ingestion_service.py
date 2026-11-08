from html.parser import HTMLParser
import ipaddress
import logging
import re
import socket
from urllib.parse import urlsplit
from urllib.request import (
    HTTPRedirectHandler,
    Request,
    build_opener
)
import xml.etree.ElementTree as ET

from ai.level_detector import detect_level
from ai.subject_classifier import classify_subject
from models.article import Article
from models.exam_category import (
    ARTICLE_QUOTA_PER_CATEGORY,
    EXAM_CATEGORY_RULES
)
from repositories.article_ingestion_repository import (
    ArticleIngestionRepository
)
from services.exam_service import ExamService

logger = logging.getLogger(__name__)

MAX_FEED_BYTES = 2_000_000
MAX_FEED_ENTRIES = 20
HTTP_TIMEOUT_SECONDS = 12


class _TextExtractor(HTMLParser):

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.ignored_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag.lower() in {"script", "style", "nav", "footer", "header"}:
            self.ignored_depth += 1
        elif tag.lower() in {"p", "br", "div", "li"} and not self.ignored_depth:
            self.parts.append(" ")
        elif tag.lower() == "img" and not self.ignored_depth:
            alt_text = dict(attrs).get("alt")
            if alt_text:
                self.parts.append(alt_text)

    def handle_endtag(self, tag):
        if tag.lower() in {"script", "style", "nav", "footer", "header"}:
            self.ignored_depth = max(0, self.ignored_depth - 1)
        elif tag.lower() in {"p", "br", "div", "li"} and not self.ignored_depth:
            self.parts.append(" ")

    def handle_data(self, data):
        if not self.ignored_depth:
            self.parts.append(data)


class _NoRedirectHandler(HTTPRedirectHandler):

    def redirect_request(self, *args, **kwargs):
        _ = args, kwargs
        return None


def _validate_public_feed_url(feed_url: str) -> None:
    parsed = urlsplit(feed_url)
    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.hostname
        or parsed.username
        or parsed.password
        or parsed.fragment
    ):
        raise ValueError("Use a public HTTP or HTTPS RSS/Atom feed URL.")

    try:
        addresses = socket.getaddrinfo(
            parsed.hostname,
            parsed.port or (443 if parsed.scheme == "https" else 80),
            type=socket.SOCK_STREAM
        )
    except OSError as error:
        raise ValueError("The feed host could not be resolved.") from error

    if not addresses or any(
        not ipaddress.ip_address(address[4][0]).is_global
        for address in addresses
    ):
        raise ValueError("The feed URL must resolve only to public IP addresses.")


def _fetch_feed(feed_url: str) -> bytes:
    _validate_public_feed_url(feed_url)
    request = Request(
        feed_url,
        headers={"User-Agent": "YKI-Reading-AI-Coach/1.0"}
    )
    opener = build_opener(_NoRedirectHandler())
    with opener.open(request, timeout=HTTP_TIMEOUT_SECONDS) as response:
        content = response.read(MAX_FEED_BYTES + 1)
    if len(content) > MAX_FEED_BYTES:
        raise ValueError("The feed exceeds the 2 MB download limit.")
    return content


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].split(":")[-1].casefold()


def _child_text(element: ET.Element, *names: str) -> str:
    children = list(element)
    for name in names:
        for child in children:
            if _local_name(child.tag) == name.casefold():
                text = "".join(child.itertext()).strip()
                if text:
                    return text
    return ""


def _entry_link(entry: ET.Element) -> str:
    for child in entry:
        if _local_name(child.tag) != "link":
            continue
        href = child.attrib.get("href")
        if href:
            return href.strip()
        if child.text and child.text.strip():
            return child.text.strip()
    return _child_text(entry, "link", "guid", "id")


def _clean_article_text(raw_content: str) -> str:
    parser = _TextExtractor()
    parser.feed(raw_content)
    parser.close()
    return re.sub(r"\s+", " ", " ".join(parser.parts)).strip()


def _word_count(content: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", content, flags=re.UNICODE))


def _parse_feed(feed_content: bytes) -> list[dict[str, str]]:
    root = ET.fromstring(feed_content)
    entries = [
        element for element in root.iter()
        if _local_name(element.tag) in {"item", "entry"}
    ][:MAX_FEED_ENTRIES]
    parsed_entries = []
    for entry in entries:
        title = _child_text(entry, "title")
        article_url = _entry_link(entry)
        raw_content = _child_text(
            entry,
            "encoded",
            "content",
            "description",
            "summary"
        )
        content = _clean_article_text(raw_content)
        if title and article_url and content:
            parsed_entries.append({
                "title": title,
                "url": article_url,
                "content": content
            })
    return parsed_entries


class ArticleIngestionService:

    @staticmethod
    def add_source_and_crawl(
            publisher: str,
            feed_url: str,
            rights_basis: str,
            permission_reference: str,
            approved_by: str,
            rights_confirmed: bool,
            exam_category: str = "utiset"
    ) -> dict:
        required_fields = {
            "publisher": publisher,
            "feed URL": feed_url,
            "license or permission": rights_basis,
            "license/permission reference": permission_reference,
            "approver": approved_by
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
                "Confirm that the license permits storing, adapting, "
                "AI processing, and displaying the full article."
            )
        if exam_category not in EXAM_CATEGORY_RULES:
            raise ValueError("Select one of the supported YKI article types.")
        _validate_public_feed_url(feed_url.strip())
        source_id = ArticleIngestionRepository.add_source(
            publisher,
            feed_url,
            rights_basis,
            permission_reference,
            approved_by,
            exam_category=exam_category
        )
        return ArticleIngestionService.crawl_source(source_id)

    @staticmethod
    def crawl_source(source_id: int) -> dict:
        source = ArticleIngestionRepository.find_source(source_id)
        if source is None:
            raise ValueError("The approved feed source was not found.")

        feed_content = _fetch_feed(source["feed_url"])
        try:
            entries = _parse_feed(feed_content)
        except ET.ParseError as error:
            raise ValueError("The URL did not return a valid RSS/Atom feed.") from error
        result = {
            "imported": [],
            "skipped": [],
            "failed": []
        }
        category_rules = EXAM_CATEGORY_RULES[source["exam_category"]]
        category_capacity = ArticleIngestionRepository.remaining_article_capacity(
            source["exam_category"]
        )

        for entry in entries:
            if ArticleIngestionRepository.has_article_url(entry["url"]):
                result["skipped"].append({
                    "title": entry["title"],
                    "reason": "Already imported."
                })
                continue

            if category_capacity <= 0:
                result["skipped"].append({
                    "title": entry["title"],
                    "reason": (
                        f"The {source['exam_category']} pool already has "
                        f"{ARTICLE_QUOTA_PER_CATEGORY} articles."
                    )
                })
                continue

            count = _word_count(entry["content"])
            if not (
                category_rules["min_words"]
                <= count
                <= category_rules["max_words"]
            ):
                result["skipped"].append({
                    "title": entry["title"],
                    "reason": (
                        f"Feed content has {count} words; accepted range "
                        f"is {category_rules['min_words']}-"
                        f"{category_rules['max_words']}."
                    )
                })
                continue

            level_result = detect_level(entry["content"])
            detected_level = level_result.get("level")
            target_level = category_rules["target_level"]
            supported_levels = {"A2", "B1", "B2", "C1"}
            if (
                detected_level not in supported_levels
                or (
                    target_level is not None
                    and detected_level != target_level
                )
            ):
                result["skipped"].append({
                    "title": entry["title"],
                    "reason": (
                        f"Could not verify the required {target_level} level."
                        if target_level
                        else "Could not verify a supported reading level."
                    )
                })
                continue

            subject_result = classify_subject(entry["content"])
            if subject_result.get("subject") is None:
                result["skipped"].append({
                    "title": entry["title"],
                    "reason": "Could not classify the article subject."
                })
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
                exam_category=source["exam_category"]
            )
            article_id = ExamService.add_approved_library_article(
                article,
                rights_basis=source["rights_basis"],
                permission_reference=source["permission_reference"],
                approved_by=source["approved_by"],
                exam_category=source["exam_category"]
            )
            if article_id is None:
                result["failed"].append({
                    "title": entry["title"],
                    "reason": "Could not generate a valid five-question exam."
                })
            else:
                result["imported"].append({
                    "title": entry["title"],
                    "article_id": article_id,
                    "word_count": count,
                    "level": article.detected_level,
                    "subject": article.subject
                })
                category_capacity -= 1

        ArticleIngestionRepository.mark_checked(source_id)
        logger.info(
            "Feed ingestion complete for source_id=%s: imported=%s skipped=%s",
            source_id,
            len(result["imported"]),
            len(result["skipped"])
        )
        return result

    @staticmethod
    def crawl_all_sources() -> list[dict]:
        results = []
        for source in ArticleIngestionRepository.list_sources():
            try:
                result = ArticleIngestionService.crawl_source(source["id"])
            except (ValueError, OSError) as error:
                results.append({
                    "publisher": source["publisher"],
                    "error": str(error)
                })
            else:
                results.append({
                    "publisher": source["publisher"],
                    **result
                })
        return results

    @staticmethod
    def list_sources() -> list[dict]:
        return ArticleIngestionRepository.list_sources()

    @staticmethod
    def remaining_article_capacity(exam_category: str) -> int:
        if exam_category not in EXAM_CATEGORY_RULES:
            raise ValueError("Unsupported sample-exam article category.")
        return ArticleIngestionRepository.remaining_article_capacity(
            exam_category
        )
