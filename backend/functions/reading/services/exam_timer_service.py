import math
import time


EXAM_DURATION_SECONDS = 30 * 60


def create_deadline(now=None, duration=EXAM_DURATION_SECONDS):
    if duration <= 0:
        raise ValueError("Exam duration must be greater than zero.")

    return (time.time() if now is None else now) + duration


def remaining_seconds(deadline, now=None):
    current_time = time.time() if now is None else now
    return max(0, math.ceil(deadline - current_time))


def format_remaining(seconds):
    remaining = max(0, int(seconds))
    minutes, seconds = divmod(remaining, 60)
    return f"{minutes:02d}:{seconds:02d}"
