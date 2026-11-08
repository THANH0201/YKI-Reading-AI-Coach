from unittest.mock import patch

from backend.ai.level_detector import detect_level


def test_detect_level_returns_supported_level_and_confidence():
    with patch(
        "ai.level_detector.ask_qwen",
        return_value={
            "success": True,
            "content": '{"level":"B2","confidence":0.82}'
        }
    ):
        assert detect_level("Finnish article") == {
            "level": "B2",
            "confidence": 0.82
        }


def test_detect_level_does_not_use_fake_level_on_provider_failure():
    with patch(
        "ai.level_detector.ask_qwen",
        return_value={"success": False, "error": "offline"}
    ):
        result = detect_level("Finnish article")

    assert result["level"] is None
    assert result["confidence"] == 0.0
    assert "error" in result


def test_detect_level_rejects_malformed_json_and_confidence():
    for content in ("not json", '{"level":"B1","confidence":"high"}'):
        with patch(
            "ai.level_detector.ask_qwen",
            return_value={"success": True, "content": content}
        ):
            assert detect_level("Finnish article")["level"] is None


def test_detect_level_rejects_out_of_range_confidence_and_non_string_level():
    for content in (
        '{"level":"B1","confidence":1.1}',
        '{"level":["B1"],"confidence":0.5}'
    ):
        with patch(
            "ai.level_detector.ask_qwen",
            return_value={"success": True, "content": content}
        ):
            assert detect_level("Finnish article")["level"] is None
