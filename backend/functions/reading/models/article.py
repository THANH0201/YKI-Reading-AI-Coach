from dataclasses import dataclass


@dataclass
class Article:
    id: int | None

    title: str

    source: str

    content: str

    detected_level: str

    level_confidence: float

    subject: str

    subject_confidence: float

    word_count: int

    created_at: str | None = None

    exam_category: str | None = None
