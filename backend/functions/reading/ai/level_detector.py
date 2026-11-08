import json

# functions/reading/ai/level_detector.py

from backend.llms.groq_client import (
    get_groq_llm
)


def detect_level(article_content: str) -> dict:

    prompt = f"""
You are a Finnish CEFR reading level evaluator.

Analyze the following Finnish article.

Instructions:
- Determine the CEFR reading level.
- Choose ONLY ONE level:
  A2, B1, B2, or C1
- Estimate your confidence score from 0.0 to 1.0

Return ONLY valid JSON.

Example:

{{
    "level": "B1",
    "confidence": 0.87
}}

Article:

{article_content}
"""

    response = ask_groq(prompt)

    if not response["success"]:
        return {
            "level": None,
            "confidence": 0.0,
            "error": response.get("error", "The level detection request failed."),
        }

    content = response["content"]

    try:
        result = json.loads(content)
        level = result.get("level")
        confidence = float(result.get("confidence", 0.0))

    except (json.JSONDecodeError, ValueError, TypeError, AttributeError):
        return {
            "level": None,
            "confidence": 0.0,
            "error": "The level detector returned invalid data.",
        }

    if (
        not isinstance(level, str)
        or level not in {"A2", "B1", "B2", "C1"}
        or not 0.0 <= confidence <= 1.0
    ):
        return {
            "level": None,
            "confidence": 0.0,
            "error": "The level detector returned an unsupported level or confidence.",
        }

    return {"level": level, "confidence": confidence}
