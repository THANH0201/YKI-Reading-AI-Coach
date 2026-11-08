import logging
import sqlite3

from backend.functions.reading.models.exam_category import EXAM_CATEGORY_RULES

from backend.sample_exam_builder.seeder import seed_sample_library
from backend.database.init_db import init_db


def main() -> None:
    init_db()
    try:
        seeded = seed_sample_library()
    except (RuntimeError, ValueError, sqlite3.Error):
        logging.getLogger(__name__).exception(
            "Could not complete the sample-library seed"
        )
        raise
    for category, count in seeded.items():
        print(f"{EXAM_CATEGORY_RULES[category]['label']}: {count} newly created")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
