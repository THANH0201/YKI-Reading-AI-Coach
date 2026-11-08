from dataclasses import dataclass
from typing import Optional


@dataclass
class Question:

    id: Optional[int]

    article_id: Optional[int]

    question_no: int

    question_type: str

    question: str

    option_a: Optional[str]

    option_b: Optional[str]

    option_c: Optional[str]

    option_d: Optional[str]

    correct_answer: str

    keywords: Optional[str]

    explanation: Optional[str]