EXAM_CATEGORY_RULES = {
    "notice": {
        "label": "Notices, advertisements, and messages",
        "min_words": 20,
        "max_words": 100,
        "target_level": None,
        "question_distribution": {"multiple_choice": 4}
    },
    "email": {
        "label": "Emails, letters, and instructions",
        "min_words": 100,
        "max_words": 250,
        "target_level": None,
        "question_distribution": {"true_false": 4}
    },
    "utiset": {
        "label": "Utiset (B2 news articles)",
        "min_words": 300,
        "max_words": 600,
        "target_level": "B2",
        "question_distribution": {"open": 5}
    },
    "selkouutiset": {
        "label": "Selkouutiset (B1 easy-language news)",
        "min_words": 300,
        "max_words": 600,
        "target_level": "B1",
        "question_distribution": {"open": 5}
    }
}

ARTICLE_QUOTA_PER_CATEGORY = 10
