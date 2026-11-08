import json
import logging
import re
import time
from typing import Any

from ai.model import ask_qwen
from models.article import Article
from models.exam_category import (
    ARTICLE_QUOTA_PER_CATEGORY,
    EXAM_CATEGORY_RULES
)
from repositories.article_ingestion_repository import (
    ArticleIngestionRepository
)
from repositories.article_repository import ArticleRepository
from repositories.question_repository import QuestionRepository

logger = logging.getLogger(__name__)

SEED_SOURCE = "Original AI-generated Finnish practice text"
SEED_RIGHTS_BASIS = "Original content generated for YKI Reading AI Coach"
SEED_PERMISSION_REFERENCE = "internal:original-ai-content:v1"
SEED_APPROVED_BY = "Project owner - original synthetic content"
SEED_BATCH_SIZES = {
    "notice": 2,
    "email": 2,
    "utiset": 1,
    "selkouutiset": 1
}
ALLOWED_SUBJECTS = {
    "Everyday life",
    "Society",
    "Work",
    "Housing",
    "Education",
    "Health",
    "Technology",
    "Environment",
    "Economy",
    "Culture",
    "Sports",
    "Politics"
}


def _strip_json_fence(content: str) -> str:
    stripped = content.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?\s*", "", stripped)
        stripped = re.sub(r"\s*```$", "", stripped)
    return stripped.strip()


def _word_count(content: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", content, flags=re.UNICODE))


def _batch_prompt(
        category: str,
        start_number: int,
        count: int
) -> str:
    rules = EXAM_CATEGORY_RULES[category]
    question_distribution = rules["question_distribution"]
    question_type, question_count = next(iter(question_distribution.items()))
    if question_type == "multiple_choice":
        question_rules = f"""
Write exactly {question_count} multiple_choice questions. Each must have
four distinct options, one correct_answer equal to one option, and a concise
explanation of no more than 12 words supported by the notice.
"""
    elif question_type == "true_false":
        question_rules = f"""
Write exactly {question_count} true_false questions. Each must have a
correct_answer of True or False and a concise explanation supported by the
message, no more than 12 words.
"""
    else:
        question_rules = f"""
Write exactly {question_count} open questions. Each must have a concise,
factually correct model answer in correct_answer, 3-5 scoring keywords in
keywords, and an explanation grounded in the article, no more than 12 words.
Keep each question and model answer concise. The five questions
should collectively cover main idea, author opinion, inference, and writer's
purpose.
"""

    level_instruction = (
        f"Use CEFR {rules['target_level']} Finnish."
        if rules["target_level"]
        else "Use natural, clear Finnish suitable for everyday adult learners."
    )
    long_text_instruction = (
        "Write exactly five paragraphs of about 80 words each (about 400 "
        "words total). The content must contain at least 300 words by the "
        "word-count rule above; shorter text will be rejected. Keep "
        "questions, model answers, and explanations very concise."
        if rules["min_words"] >= 300
        else "Keep the text close to the minimum word limit to fit the "
        "response budget."
    )
    return f"""
Create {count} completely original Finnish YKI practice texts numbered
{start_number} through {start_number + count - 1}. These are fictional
learning materials, not news reports and not copied or adapted from any
publisher, website, real event, or known article. Do not imitate a named
publication. Use varied settings and details. Do not mention this prompt.

Category: {rules['label']}.
Each content field must contain {rules['min_words']}-{rules['max_words']}
Finnish words, counting the text only (not its title or questions).
{long_text_instruction}
{level_instruction}

Subject must be exactly one of: {", ".join(sorted(ALLOWED_SUBJECTS))}.
{question_rules}
Return a JSON object with one field named "articles", containing an array of
exactly {count} objects. Every article object must have: number (integer),
title (Finnish string), content (Finnish string), subject (one allowed
subject), and questions (array). Each question must have: type, question,
correct_answer, explanation; multiple_choice additionally has options (four
strings), open additionally has keywords (3-5 strings). Do not include
Markdown or any text outside the JSON object.
"""


def _validate_questions(
        category: str,
        questions: Any
) -> list[dict]:
    if not isinstance(questions, list):
        raise ValueError(f"{category}: questions must be a list.")
    distribution = EXAM_CATEGORY_RULES[category]["question_distribution"]
    if len(questions) != sum(distribution.values()):
        raise ValueError(f"{category}: incorrect question count.")

    actual_counts: dict[str, int] = {}
    for question in questions:
        if not isinstance(question, dict):
            raise ValueError(f"{category}: invalid question object.")
        question_type = question.get("type")
        if question_type not in distribution:
            raise ValueError(
                f"{category}: unsupported question type {question_type!r}."
            )
        actual_counts[question_type] = (
            actual_counts.get(question_type, 0) + 1
        )
        if not isinstance(question.get("question"), str) or not question[
            "question"
        ].strip():
            raise ValueError(f"{category}: a question is empty.")
        if not isinstance(question.get("correct_answer"), str) or not question[
            "correct_answer"
        ].strip():
            raise ValueError(f"{category}: a question has no answer key.")
        if not isinstance(question.get("explanation"), str) or not question[
            "explanation"
        ].strip():
            raise ValueError(f"{category}: a question has no explanation.")

        if question_type == "multiple_choice":
            options = question.get("options")
            if (
                not isinstance(options, list)
                or len(options) != 4
                or len({option.casefold() for option in options
                        if isinstance(option, str)}) != 4
                or not all(
                    isinstance(option, str) and option.strip()
                    for option in options
                )
                or question["correct_answer"] not in options
            ):
                raise ValueError(
                    f"{category}: invalid multiple-choice options or answer."
                )
        elif question_type == "true_false":
            answer = question["correct_answer"].strip().casefold()
            if answer not in {"true", "false"}:
                raise ValueError(f"{category}: invalid true/false answer.")
            question["correct_answer"] = answer.title()
        else:
            keywords = question.get("keywords")
            if (
                not isinstance(keywords, list)
                or not 3 <= len(keywords) <= 5
                or not all(
                    isinstance(keyword, str) and keyword.strip()
                    for keyword in keywords
                )
            ):
                raise ValueError(f"{category}: invalid open-answer keywords.")

    if actual_counts != distribution:
        raise ValueError(f"{category}: question distribution is invalid.")
    return questions


def _request_content(
        prompt: str,
        category: str,
        start_number: int,
        json_mode: bool = True
) -> str:
    response = None
    for attempt in range(3):
        response = ask_qwen(
            prompt,
            temperature=0.5,
            response_format=(
                {"type": "json_object"} if json_mode else None
            ),
            max_completion_tokens=950
        )
        if response.get("success"):
            break
        error_message = str(response.get("error", "unknown error"))
        if (
            "rate_limit_exceeded" not in error_message
            and "tokens per minute" not in error_message.casefold()
        ):
            break
        if attempt < 2:
            logger.warning(
                "AI output token limit reached; waiting before retrying %s",
                category
            )
            time.sleep(65)
    if not response.get("success"):
        raise RuntimeError(
            f"AI generation failed for {category} batch "
            f"{start_number}: {response.get('error', 'unknown error')}"
        )
    content = response.get("content")
    if not isinstance(content, str) or not content.strip():
        raise RuntimeError(
            f"AI returned no content for {category} batch {start_number}."
        )
    return content


def _request_json(
        prompt: str,
        category: str,
        start_number: int
) -> dict:
    content = _request_content(prompt, category, start_number)
    try:
        response_data = json.loads(_strip_json_fence(content))
    except json.JSONDecodeError as error:
        raise RuntimeError(
            f"AI returned invalid JSON for {category} batch {start_number}."
        ) from error
    if not isinstance(response_data, dict):
        raise RuntimeError(
            f"AI returned an invalid object for {category} batch {start_number}."
        )
    return response_data


def _generate_long_article(
        category: str,
        article_number: int
) -> dict:
    rules = EXAM_CATEGORY_RULES[category]
    level_instruction = f"Use CEFR {rules['target_level']} Finnish."
    content = _request_content(
        f"""
Create one completely original fictional Finnish YKI practice article.
It must not be copied or adapted from any publisher, website, real event,
or known article. Do not imitate a named publication.
Category: {rules['label']}. {level_instruction}
Write exactly five paragraphs of about 80-85 words each (about 400 words).
The article body
must contain 300-600 Finnish words. Do not include questions, answers, or a
word count. Start the response with these three lines:
TITLE: [short Finnish title]
SUBJECT: [one exact subject from this list: {", ".join(sorted(ALLOWED_SUBJECTS))}]
CONTENT:
Then write only the five-paragraph article. Do not use Markdown fences.
""",
        category,
        article_number,
        json_mode=False
    )
    lines = content.strip().splitlines()
    if len(lines) < 4 or not lines[0].startswith("TITLE: ") or not lines[
        1
    ].startswith("SUBJECT: ") or lines[2].strip() != "CONTENT:":
        raise ValueError(f"{category}: AI returned an invalid article format.")
    article_data = {
        "title": lines[0][len("TITLE: "):].strip(),
        "subject": lines[1][len("SUBJECT: "):].strip(),
        "content": "\n".join(lines[3:]).strip()
    }
    for field in ("title", "content", "subject"):
        if not isinstance(article_data.get(field), str) or not article_data[
            field
        ].strip():
            raise ValueError(f"{category}: generated {field} is empty.")
    if article_data["subject"] not in ALLOWED_SUBJECTS:
        raise ValueError(
            f"{category}: unsupported subject {article_data['subject']!r}."
        )
    words = _word_count(article_data["content"])
    if words < rules["min_words"]:
        continuation = _request_content(
            f"""
Continue this original Finnish practice article with one final paragraph.
Write only the additional paragraph, approximately 70 words, and make it
continue naturally without repeating existing facts. The completed article
must contain at least {rules['min_words']} words and no more than
{rules['max_words']} words.
Article so far:
{article_data['content']}
""",
            category,
            article_number,
            json_mode=False
        ).strip()
        article_data["content"] = (
            f"{article_data['content']}\n\n{continuation}"
        )
        words = _word_count(article_data["content"])
    if not rules["min_words"] <= words <= rules["max_words"]:
        raise ValueError(
            f"{category} article {article_number} has {words} words; "
            f"expected {rules['min_words']}-{rules['max_words']}."
        )

    question_data = _request_json(
        f"""
Write exactly five open-ended Finnish reading-comprehension questions for
this original practice article. Cover the main idea, author opinion,
inference, and writer's purpose. Each question must have a concise,
factually correct model answer in correct_answer, 3-5 scoring keywords in
keywords, and an explanation grounded in the article of no more than
12 words. Keep all questions and answers concise.
Article:
{article_data['content']}
Return a JSON object with one field named "questions", containing an array
of exactly five objects. Each object must have type "open", question,
correct_answer, explanation, and keywords. Do not include Markdown or text
outside the JSON object.
""",
        category,
        article_number
    )
    article_data["questions"] = _validate_questions(
        category,
        question_data.get("questions")
    )
    article_data["number"] = article_number
    return article_data


def _generate_batch(
        category: str,
        start_number: int,
        count: int
) -> list[dict]:
    if category in {"utiset", "selkouutiset"}:
        if count != 1:
            raise ValueError(
                f"{category}: long articles must be generated one at a time."
            )
        return [_generate_long_article(category, start_number)]

    prompt = _batch_prompt(category, start_number, count)
    response_data = _request_json(prompt, category, start_number)
    articles = response_data.get("articles")
    if not isinstance(articles, list) or len(articles) != count:
        raise RuntimeError(
            f"AI returned the wrong number of {category} texts."
        )

    rules = EXAM_CATEGORY_RULES[category]
    for offset, article_data in enumerate(articles):
        expected_number = start_number + offset
        if not isinstance(article_data, dict):
            raise ValueError(f"{category}: invalid generated article.")
        if article_data.get("number") != expected_number:
            raise ValueError(
                f"{category}: expected generated article {expected_number}."
            )
        for field in ("title", "content", "subject"):
            if not isinstance(article_data.get(field), str) or not article_data[
                field
            ].strip():
                raise ValueError(f"{category}: generated {field} is empty.")
        if article_data["subject"] not in ALLOWED_SUBJECTS:
            raise ValueError(
                f"{category}: unsupported subject "
                f"{article_data['subject']!r}."
            )
        words = _word_count(article_data["content"])
        if not rules["min_words"] <= words <= rules["max_words"]:
            raise ValueError(
                f"{category} article {expected_number} has {words} words; "
                f"expected {rules['min_words']}-{rules['max_words']}."
            )
        article_data["questions"] = _validate_questions(
            category,
            article_data.get("questions")
        )
    return articles


def _generate_batch_with_fallback(
        category: str,
        start_number: int,
        count: int
) -> list[dict]:
    try:
        return _generate_batch(category, start_number, count)
    except (RuntimeError, ValueError):
        if count == 1:
            raise
        smaller_count = count // 2
        logger.warning(
            "Retrying invalid %s batch as smaller requests",
            category
        )
        return [
            *_generate_batch_with_fallback(
                category,
                start_number,
                smaller_count
            ),
            *_generate_batch_with_fallback(
                category,
                start_number + smaller_count,
                count - smaller_count
            )
        ]


def _save_generated_article(category: str, article_data: dict) -> int:
    rules = EXAM_CATEGORY_RULES[category]
    level = rules["target_level"] or "B1"
    content = article_data["content"].strip()
    article = Article(
        id=None,
        title=article_data["title"].strip(),
        source=(
            f"{SEED_SOURCE} ({category} #{article_data['number']})"
        ),
        content=content,
        detected_level=level,
        level_confidence=0.7,
        subject=article_data["subject"],
        subject_confidence=0.7,
        word_count=_word_count(content),
        exam_category=category
    )
    article_id = ArticleRepository.save_approved_exam_article(
        article,
        rights_basis=SEED_RIGHTS_BASIS,
        permission_reference=SEED_PERMISSION_REFERENCE,
        approved_by=SEED_APPROVED_BY,
        exam_category=category
    )
    QuestionRepository.save_all(article_id, article_data["questions"])
    return article_id


def seed_sample_library() -> dict[str, int]:
    seeded = {}
    for category in EXAM_CATEGORY_RULES:
        remaining = ArticleIngestionRepository.remaining_article_capacity(
            category
        )
        created = 0
        while created < remaining:
            batch_size = min(
                SEED_BATCH_SIZES[category],
                remaining - created
            )
            start_number = (
                ArticleIngestionRepository.count_approved_articles(category)
                + created
                + 1
            )
            generated_articles = _generate_batch_with_fallback(
                category,
                start_number,
                batch_size
            )
            for article_data in generated_articles:
                _save_generated_article(category, article_data)
                created += 1
                logger.info(
                    "Seeded %s article %s/%s",
                    category,
                    start_number + created - 1,
                    ARTICLE_QUOTA_PER_CATEGORY
                )
        seeded[category] = created
    return seeded
