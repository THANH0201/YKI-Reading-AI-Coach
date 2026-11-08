import json

from backend.ai.model import ask_qwen

def classify_subject(article_content: str) -> dict:
    prompt = f"""
You are an expert Finnish news classifier.

Analyze the article and determine its primary subject.

Choose ONLY ONE primary category:

- Everyday life (shopping, public transport, hobbies, local events)
- Society
- Work
- Housing (renting, housing companies, moving, apartment repairs)
- Education
- Health
- Technology
- Environment
- Economy
- Culture
- Sports
- Politics

Return ONLY valid JSON.

Example:

{{
    "subject": "Technology",
    "confidence": 0.91
}}

Article:

{article_content}
"""

    response = ask_qwen(prompt)

    if not response["success"]:
        return {
            "subject": None,
            "confidence": 0.0,
            "error": response.get(
                "error",
                "The subject classification request failed."
            )
        }

    response_content = response.get("content")
    if not isinstance(response_content, str):
        return {
            "subject": None,
            "confidence": 0.0,
            "error": "The subject classifier returned no valid content."
        }

    content = response_content.replace("```json", "").replace("```", "").strip()
    try:
        result = json.loads(content)
        subject = result.get("subject")
        confidence = float(result.get("confidence", 0.0))
    except (json.JSONDecodeError, TypeError, ValueError, AttributeError):
        return {
            "subject": None,
            "confidence": 0.0,
            "error": "The subject classifier returned invalid data."
        }

    allowed_subjects = {
        "Everyday life", "Society", "Work", "Housing", "Education",
        "Health", "Technology", "Environment", "Economy", "Culture",
        "Sports", "Politics"
    }
    if (
        not isinstance(subject, str)
        or subject not in allowed_subjects
        or not 0.0 <= confidence <= 1.0
    ):
        return {
            "subject": None,
            "confidence": 0.0,
            "error": "The subject classifier returned an unsupported subject or confidence."
        }

    return {
        "subject": subject,
        "confidence": confidence
    }