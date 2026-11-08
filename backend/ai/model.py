import os
import logging

try:
    from dotenv import load_dotenv  # pyright: ignore[reportMissingImports]
except ImportError:
    def load_dotenv() -> bool:
        return False
try:
    from openai import OpenAI  # pyright: ignore[reportMissingImports]
except ImportError:
    OpenAI = None

load_dotenv()

logger = logging.getLogger(__name__)

client = (
    OpenAI(
        api_key=os.getenv("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1"
    )
    if OpenAI is not None
    else None
)


def ask_qwen(
        prompt: str,
        temperature: float = 0.3,
        response_format: dict | None = None,
        max_completion_tokens: int | None = None
) -> dict:

    try:
        if client is None:
            raise RuntimeError("The openai package is not installed")

        request_parameters = {
            "model": "qwen/qwen3.8-27b",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": temperature
        }
        if response_format is not None:
            request_parameters["response_format"] = response_format
        if max_completion_tokens is not None:
            request_parameters["max_completion_tokens"] = (
                max_completion_tokens
            )
        response = client.chat.completions.create(**request_parameters)

        content = (
            response
            .choices[0]
            .message
            .content
        )

        return {
            "success": True,
            "content": content
        }

    except Exception as e:

        logger.exception(
            "Qwen API error"
        )

        return {
            "success": False,
            "content": None,
            "error": str(e)
        }
