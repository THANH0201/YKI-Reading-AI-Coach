import json

from backend.ai.model import ask_qwen


def analyze_writing(text: str) -> dict:
    if not isinstance(text, str) or not text.strip():
        return {
            "success": False,
            "message": "Please enter your Finnish writing first."
        }

    prompt = f"""
You are a Finnish writing coach for adult learners preparing for the YKI
language examination.

Analyze the learner's Finnish text. Estimate whether it is closer to CEFR B1
or B2, and give supportive, specific feedback. Do not claim that this is an
official CEFR or YKI score.

Return ONLY a JSON object with exactly these fields:
- estimated_level: "B1" or "B2"
- assessment: a concise overall assessment in Vietnamese
- strengths: an array of concise Vietnamese strings
- corrections: an array of objects with "original", "corrected", and
  "explanation" string fields. Identify genuine spelling or grammar errors;
  explanations must be in Vietnamese.
- sentence_suggestions: an array of objects with "original", "suggestion",
  and "explanation" string fields. Suggest clearer sentence structure and
  vocabulary appropriate to the learner's estimated B1/B2 level; explanations
  must be in Vietnamese. Do not present optional style improvements as errors.
- revised_text: a complete suggested version in Finnish at the estimated
  level, preserving the learner's meaning.

Use empty arrays when there are no corrections or suggestions. Do not invent
content that is not in the learner's text.

Learner's text:
{text}
"""

    response = ask_qwen(
        prompt,
        response_format={"type": "json_object"}
    )
    if not response.get("success"):
        return {
            "success": False,
            "message": "The writing analysis service is unavailable. Please try again."
        }

    content = response.get("content")
    if not isinstance(content, str):
        return {
            "success": False,
            "message": "The writing analyzer returned no valid result."
        }

    try:
        analysis = json.loads(content)
    except json.JSONDecodeError:
        return {
            "success": False,
            "message": "The writing analyzer returned invalid data."
        }

    if not isinstance(analysis, dict):
        return {
            "success": False,
            "message": "The writing analyzer returned invalid data."
        }

    corrections = analysis.get("corrections")
    suggestions = analysis.get("sentence_suggestions")
    strengths = analysis.get("strengths")
    estimated_level = analysis.get("estimated_level")
    if (
        not isinstance(estimated_level, str)
        or estimated_level not in {"B1", "B2"}
        or not isinstance(analysis.get("assessment"), str)
        or not analysis["assessment"].strip()
        or not isinstance(strengths, list)
        or not all(isinstance(item, str) and item.strip() for item in strengths)
        or not isinstance(corrections, list)
        or not all(
            isinstance(item, dict)
            and all(
                isinstance(item.get(key), str) and item[key].strip()
                for key in ("original", "corrected", "explanation")
            )
            for item in corrections
        )
        or not isinstance(suggestions, list)
        or not all(
            isinstance(item, dict)
            and all(
                isinstance(item.get(key), str) and item[key].strip()
                for key in ("original", "suggestion", "explanation")
            )
            for item in suggestions
        )
        or not isinstance(analysis.get("revised_text"), str)
        or not analysis["revised_text"].strip()
    ):
        return {
            "success": False,
            "message": "The writing analyzer returned incomplete or invalid data."
        }

    return {"success": True, "analysis": analysis}
