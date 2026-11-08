from unittest.mock import patch

from backend.ai.subject_classifier import classify_subject


def test_subject_classifier_parses_valid_json():
    with patch(
        "ai.subject_classifier.ask_qwen",
        return_value={
            "success": True,
            "content": '```json\n{"subject":"Technology","confidence":0.9}\n```'
        }
    ):
        assert classify_subject("Article") == {
            "subject": "Technology",
            "confidence": 0.9
        }


def test_subject_classifier_supports_yki_everyday_and_housing_topics():
    for subject in ("Everyday life", "Housing"):
        with patch(
            "ai.subject_classifier.ask_qwen",
            return_value={
                "success": True,
                "content": (
                    f'{{"subject":"{subject}","confidence":0.8}}'
                )
            }
        ):
            assert classify_subject("Article")["subject"] == subject


def test_subject_classifier_reports_provider_and_data_errors():
    with patch(
        "ai.subject_classifier.ask_qwen",
        return_value={"success": False, "error": "offline"}
    ):
        assert classify_subject("Article")["subject"] is None


def test_subject_classifier_rejects_missing_content_and_invalid_confidence():
    with patch(
        "ai.subject_classifier.ask_qwen",
        return_value={"success": True, "content": None}
    ):
        assert classify_subject("Article")["subject"] is None

    with patch(
        "ai.subject_classifier.ask_qwen",
        return_value={
            "success": True,
            "content": '{"subject":"Society","confidence":2}'
        }
    ):
        assert classify_subject("Article")["subject"] is None

    with patch(
        "ai.subject_classifier.ask_qwen",
        return_value={"success": True, "content": "not json"}
    ):
        assert classify_subject("Article")["subject"] is None

    with patch(
        "ai.subject_classifier.ask_qwen",
        return_value={
            "success": True,
            "content": '{"subject":"Unknown","confidence":0.5}'
        }
    ):
        assert classify_subject("Article")["subject"] is None
