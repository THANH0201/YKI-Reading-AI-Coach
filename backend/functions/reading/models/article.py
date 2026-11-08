from dataclasses import dataclass
from typing import Optional


@dataclass
class Article:

    id: Optional[int]

    title: str

    source: str

    content: str

    detected_level: str

    level_confidence: float

    subject: str

    subject_confidence: float

    word_count: int

    created_at: Optional[str] = None

    exam_category: Optional[str] = None