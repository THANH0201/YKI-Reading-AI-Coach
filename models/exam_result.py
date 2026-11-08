from dataclasses import dataclass
from typing import Optional


@dataclass
class ExamResult:

    id: Optional[int]

    article_id: Optional[int]

    score: float

    correct_answers: int

    total_questions: int

    created_at: Optional[str] = None