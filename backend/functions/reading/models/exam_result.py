from dataclasses import dataclass


@dataclass
class ExamResult:
    id: int | None

    article_id: int | None

    score: float

    correct_answers: int

    total_questions: int

    created_at: str | None = None
