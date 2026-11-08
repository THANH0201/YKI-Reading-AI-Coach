from dataclasses import dataclass


@dataclass
class UserAnswer:
    id: int | None

    exam_result_id: int

    question_id: int

    selected_answer: str

    is_correct: bool

    created_at: str | None = None
