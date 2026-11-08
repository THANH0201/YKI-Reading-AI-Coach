from unittest.mock import patch

import pytest

from repositories.article_ingestion_repository import (
    ArticleIngestionRepository
)
from services.article_ingestion_service import (
    ArticleIngestionService,
    _parse_feed,
    _word_count
)


def _feed(content, link="https://publisher.example/article/1"):
    return f"""<?xml version="1.0"?>
    <rss version="2.0"
         xmlns:content="http://purl.org/rss/1.0/modules/content/">
      <channel>
        <item>
          <title>Finnish article</title>
          <link>{link}</link>
          <description>Short summary.</description>
          <content:encoded><![CDATA[{content}]]></content:encoded>
        </item>
      </channel>
    </rss>
    """.encode()


def _eligible_content():
    return "<p>" + " ".join(
        f"Finnish article word {number} discusses daily life."
        for number in range(55)
    ) + "</p>"


def _questions():
    return [
        {
            "type": "open",
            "question": f"Question {number}?",
            "correct_answer": f"Model answer {number}.",
            "keywords": ["työ", "koti", "Suomi"]
        }
        for number in range(1, 6)
    ]


def test_feed_parser_prefers_full_content_and_extracts_plain_text():
    entries = _parse_feed(_feed(
        "<article><p>" + ("Finnish text. " * 310) +
        "<script>hidden injected text</script></p></article>"
    ))

    assert len(entries) == 1
    assert entries[0]["title"] == "Finnish article"
    assert entries[0]["url"] == "https://publisher.example/article/1"
    assert "hidden injected text" not in entries[0]["content"]
    assert _word_count(entries[0]["content"]) == 620


def test_feed_crawl_requires_explicit_reuse_rights_confirmation(database):
    with patch(
        "services.article_ingestion_service._validate_public_feed_url"
    ):
        with pytest.raises(ValueError, match="Confirm that the license"):
            ArticleIngestionService.add_source_and_crawl(
                publisher="Publisher",
                feed_url="https://publisher.example/feed.xml",
                rights_basis="CC BY 4.0",
                permission_reference="https://publisher.example/license",
                approved_by="Reviewer",
                rights_confirmed=False
            )

    assert ArticleIngestionRepository.list_sources() == []


def test_crawl_imports_eligible_full_text_and_skips_duplicate(database):
    content = _eligible_content()
    with (
        patch(
            "services.article_ingestion_service._validate_public_feed_url"
        ),
        patch(
            "services.article_ingestion_service._fetch_feed",
            return_value=_feed(content)
        ),
        patch(
            "services.article_ingestion_service.detect_level",
            return_value={"level": "B2", "confidence": 0.9}
        ),
        patch(
            "services.article_ingestion_service.classify_subject",
            return_value={"subject": "Society", "confidence": 0.9}
        ),
        patch(
            "services.exam_service.generate_questions",
            return_value=_questions()
        )
    ):
        first_result = ArticleIngestionService.add_source_and_crawl(
            publisher="Licensed Publisher",
            feed_url="https://publisher.example/feed.xml",
            rights_basis="CC BY 4.0",
            permission_reference="https://publisher.example/license",
            approved_by="Reviewer",
            rights_confirmed=True,
            exam_category="utiset"
        )
        second_result = ArticleIngestionService.crawl_source(
            ArticleIngestionRepository.list_sources()[0]["id"]
        )

    assert len(first_result["imported"]) == 1
    assert first_result["imported"][0]["word_count"] == 385
    assert first_result["imported"][0]["level"] == "B2"
    assert ArticleIngestionRepository.list_sources()[0]["exam_category"] == (
        "utiset"
    )
    assert second_result["skipped"] == [{
        "title": "Finnish article",
        "reason": "Already imported."
    }]
    assert first_result["imported"][0]["article_id"] is not None
    assert ArticleIngestionRepository.remaining_article_capacity(
        "utiset"
    ) == 29


def test_crawl_skips_short_feed_excerpt_without_ai_calls(database):
    with (
        patch(
            "services.article_ingestion_service._validate_public_feed_url"
        ),
        patch(
            "services.article_ingestion_service._fetch_feed",
            return_value=_feed("<p>Only a short excerpt.</p>")
        ),
        patch(
            "services.article_ingestion_service.detect_level"
        ) as detect_level
    ):
        result = ArticleIngestionService.add_source_and_crawl(
            publisher="Licensed Publisher",
            feed_url="https://publisher.example/feed.xml",
            rights_basis="Written permission",
            permission_reference="permission-ref-001",
            approved_by="Reviewer",
            rights_confirmed=True
        )

    detect_level.assert_not_called()
    assert result["imported"] == []
    assert result["skipped"][0]["reason"] == (
        "Feed content has 4 words; accepted range is 300-600."
    )


def test_feed_url_rejects_non_public_host(monkeypatch):
    import services.article_ingestion_service as ingestion

    monkeypatch.setattr(
        ingestion.socket,
        "getaddrinfo",
        lambda *args, **kwargs: [
            (None, None, None, None, ("127.0.0.1", 80))
        ]
    )

    with pytest.raises(ValueError, match="public IP"):
        ingestion._validate_public_feed_url(
            "http://localhost/private-feed.xml"
        )
