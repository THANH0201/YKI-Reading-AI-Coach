from dataclasses import dataclass


@dataclass
class Question:
    id: int | None

    article_id: int | None

    question_no: int

    question_type: str

    question: str

    option_a: str | None

    option_b: str | None

    option_c: str | None

    option_d: str | None

    correct_answer: str

    keywords: str | None

    explanation: str | None
