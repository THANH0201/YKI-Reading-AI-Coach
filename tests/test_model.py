import builtins
import runpy
from types import SimpleNamespace
from unittest.mock import patch
from pathlib import Path

from backend.ai import model


def test_ask_qwen_returns_provider_response():
    captured_request = {}

    completion = SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(content="response")
            )
        ]
    )
    fake_client = SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(
                create=lambda **kwargs: (
                    captured_request.update(kwargs) or completion
                )
            )
        )
    )

    with patch.object(model, "client", fake_client):
        assert model.ask_qwen(
            "prompt",
            response_format={"type": "json_object"},
            max_completion_tokens=8192
        ) == {
            "success": True,
            "content": "response"
        }
    assert captured_request["response_format"] == {"type": "json_object"}
    assert captured_request["max_completion_tokens"] == 8192


def test_ask_qwen_reports_provider_failure():
    def fail_request(**kwargs):
        raise RuntimeError("offline")

    fake_client = SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(create=fail_request)
        )
    )
    with (
        patch.object(model, "client", fake_client),
        patch.object(model.logger, "exception")
    ):
        result = model.ask_qwen("prompt")

    assert result["success"] is False
    assert "offline" in result["error"]


def test_ask_qwen_reports_missing_client():
    with patch.object(model, "client", None), patch.object(model.logger, "exception"):
        result = model.ask_qwen("prompt")

    assert result["success"] is False
    assert "not installed" in result["error"]


def test_model_module_loads_without_optional_packages():
    real_import = builtins.__import__

    def import_without_optional_packages(name, *args, **kwargs):
        if name in {"dotenv", "openai"}:
            raise ImportError(f"{name} unavailable")
        return real_import(name, *args, **kwargs)

    module_path = Path(__file__).resolve().parents[1] / "ai" / "model.py"
    with patch("builtins.__import__", side_effect=import_without_optional_packages):
        namespace = runpy.run_path(str(module_path))

    assert namespace["client"] is None
    assert namespace["load_dotenv"]() is False
