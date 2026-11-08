import pytest

from backend.ai_neural_networks.reading.services.exam_timer_service import (
    EXAM_DURATION_SECONDS,
    create_deadline,
    format_remaining,
    remaining_seconds,
)


def test_create_deadline_defaults_to_thirty_minutes():
    assert create_deadline(now=100) == 100 + EXAM_DURATION_SECONDS


def test_create_deadline_rejects_non_positive_duration():
    with pytest.raises(ValueError, match="greater than zero"):
        create_deadline(now=100, duration=0)


@pytest.mark.parametrize(
    ("deadline", "now", "expected"),
    [
        (100, 100, 0),
        (101, 100, 1),
        (101.1, 100, 2),
        (99, 100, 0)
    ]
)
def test_remaining_seconds_counts_down_and_clamps_to_zero(deadline, now, expected):
    assert remaining_seconds(deadline, now=now) == expected


@pytest.mark.parametrize(
    ("seconds", "expected"),
    [
        (1800, "30:00"),
        (65, "01:05"),
        (5, "00:05"),
        (0, "00:00"),
        (-1, "00:00")
    ]
)
def test_format_remaining_displays_minutes_and_seconds(seconds, expected):
    assert format_remaining(seconds) == expected
