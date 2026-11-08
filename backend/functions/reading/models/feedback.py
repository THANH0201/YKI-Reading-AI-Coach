from dataclasses import dataclass


@dataclass
class Feedback:
    overall_feedback: str

    reading_level: str

    strengths: list

    weaknesses: list

    recommendations: list

    next_goal: str
