import json
from unittest.mock import patch

from backend.ai.writing_analyzer import analyze_writing


def valid_analysis():
    return {
        "estimated_level": "B1",
        "assessment": "Bài viết dễ hiểu.",
        "strengths": ["Nội dung rõ ràng."],
        "corrections": [{
            "original": "Minä menee",
            "corrected": "Minä menen",
            "explanation": "Động từ cần chia theo ngôi minä."
        }],
        "sentence_suggestions": [{
            "original": "Minä opiskelen suomea. Se on vaikeaa.",
            "suggestion": "Opiskelen suomea, vaikka se on vaikeaa.",
            "explanation": "Có thể nối hai ý liên quan bằng vaikka."
        }],
        "revised_text": "Opiskelen suomea, vaikka se on vaikeaa."
    }


def test_analyze_writing_returns_validated_feedback():
    with patch(
        "ai.writing_analyzer.ask_qwen",
        return_value={
            "success": True,
            "content": json.dumps(valid_analysis(), ensure_ascii=False)
        }
    ) as ask_qwen:
        result = analyze_writing("Minä menee kouluun.")

    assert result == {"success": True, "analysis": valid_analysis()}
    assert ask_qwen.call_args.kwargs == {
        "response_format": {"type": "json_object"}
    }
    assert "B1" in ask_qwen.call_args.args[0]
    assert "Minä menee kouluun." in ask_qwen.call_args.args[0]


def test_analyze_writing_rejects_empty_text_without_calling_model():
    with patch("ai.writing_analyzer.ask_qwen") as ask_qwen:
        result = analyze_writing("  ")

    assert result == {
        "success": False,
        "message": "Please enter your Finnish writing first."
    }
    ask_qwen.assert_not_called()


def test_analyze_writing_surfaces_invalid_model_output():
    with patch(
        "ai.writing_analyzer.ask_qwen",
        return_value={
            "success": True,
            "content": '{"estimated_level":[]}'
        }
    ):
        result = analyze_writing("Kirjoitan suomeksi.")

    assert result["success"] is False
    assert "incomplete or invalid" in result["message"]
