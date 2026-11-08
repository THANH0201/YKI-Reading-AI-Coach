from dataclasses import dataclass
from typing import Optional


@dataclass
class UserAnswer:

    id: Optional[int]

    exam_result_id: int

    question_id: int

    selected_answer: str

    is_correct: bool

    created_at: Optional[str] = None