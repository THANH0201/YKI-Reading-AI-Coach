from backend.database.db import get_connection


def init_db():

    conn = get_connection()
    cursor = conn.cursor()

    # =========================
    # ARTICLES
    # =========================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS articles(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        title TEXT NOT NULL,
        source TEXT NOT NULL,
        content TEXT NOT NULL,

        detected_level TEXT,
        level_confidence REAL,

        subject TEXT,
        subject_confidence REAL,

        word_count INTEGER,

        status TEXT DEFAULT 'ANALYZED',
        reuse_approved INTEGER NOT NULL DEFAULT 0
            CHECK(reuse_approved IN (0, 1)),
        rights_basis TEXT,
        permission_reference TEXT,
        reuse_approved_by TEXT,
        reuse_approved_at TIMESTAMP,
        exam_category TEXT,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS article_ingestion_sources(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        publisher TEXT NOT NULL,
        feed_url TEXT NOT NULL UNIQUE,
        rights_basis TEXT NOT NULL,
        permission_reference TEXT NOT NULL,
        approved_by TEXT NOT NULL,
        exam_category TEXT NOT NULL DEFAULT 'utiset',
        active INTEGER NOT NULL DEFAULT 1
            CHECK(active IN (0, 1)),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_checked_at TIMESTAMP
    )
    """)

    article_columns = {
        row[1]
        for row in cursor.execute("PRAGMA table_info(articles)")
    }
    for column, definition in (
        ("reuse_approved", "INTEGER NOT NULL DEFAULT 0"),
        ("rights_basis", "TEXT"),
        ("permission_reference", "TEXT"),
        ("reuse_approved_by", "TEXT"),
        ("reuse_approved_at", "TIMESTAMP"),
        ("exam_category", "TEXT")
    ):
        if column not in article_columns:
            cursor.execute(
                f"ALTER TABLE articles ADD COLUMN {column} {definition}"
            )

    ingestion_source_columns = {
        row[1]
        for row in cursor.execute(
            "PRAGMA table_info(article_ingestion_sources)"
        )
    }
    if "exam_category" not in ingestion_source_columns:
        cursor.execute("""
            ALTER TABLE article_ingestion_sources
            ADD COLUMN exam_category TEXT NOT NULL DEFAULT 'utiset'
        """)

    # =========================
    # QUESTIONS
    # =========================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS questions(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        article_id INTEGER NOT NULL,

        question_no INTEGER NOT NULL,

        question_type TEXT NOT NULL,

        question TEXT NOT NULL,

        option_a TEXT,
        option_b TEXT,
        option_c TEXT,
        option_d TEXT,

        correct_answer TEXT,

        keywords TEXT,

        explanation TEXT,

        FOREIGN KEY(article_id)
            REFERENCES articles(id)
    )
    """)

    # =========================
    # EXAM RESULTS
    # =========================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS exam_results(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        article_id INTEGER NOT NULL,

        correct_answers INTEGER,

        total_questions INTEGER,

        score REAL,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY(article_id)
            REFERENCES articles(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS exam_result_articles(
        exam_result_id INTEGER NOT NULL,
        article_id INTEGER NOT NULL,
        article_order INTEGER NOT NULL,
        PRIMARY KEY(exam_result_id, article_id),
        FOREIGN KEY(exam_result_id)
            REFERENCES exam_results(id)
            ON DELETE CASCADE,
        FOREIGN KEY(article_id)
            REFERENCES articles(id)
    )
    """)

    # =========================
    # USER ANSWERS
    # =========================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_answers(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        exam_result_id INTEGER NOT NULL,

        question_id INTEGER NOT NULL,

        selected_answer TEXT,

        is_correct INTEGER,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY(exam_result_id)
            REFERENCES exam_results(id),

        FOREIGN KEY(question_id)
            REFERENCES questions(id)
    )
    """)

    # =========================
    # VOCABULARY TRANSLATIONS
    # =========================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vocabulary_translations(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        phrase_key TEXT NOT NULL,
        phrase TEXT NOT NULL,
        source_language TEXT NOT NULL,
        target_language TEXT NOT NULL,
        translation TEXT NOT NULL,
        provider TEXT NOT NULL,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        UNIQUE(phrase_key, source_language, target_language)
    )
    """)

    # =========================
    # VOCABULARY WORD ANALYSES
    # =========================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vocabulary_words(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        word_key TEXT NOT NULL,
        word_form TEXT NOT NULL,
        lemma TEXT NOT NULL,
        part_of_speech TEXT NOT NULL,
        meaning TEXT,
        noun_type TEXT,
        verb_type INTEGER CHECK(verb_type BETWEEN 1 AND 6 OR verb_type IS NULL),

        suffixes TEXT NOT NULL DEFAULT '[]',
        grammatical_features TEXT NOT NULL DEFAULT '{}',
        stem_changes TEXT NOT NULL DEFAULT '[]',

        subject TEXT,
        article_id INTEGER,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY(article_id)
            REFERENCES articles(id)
    )
    """)

    vocabulary_columns = {
        row[1]
        for row in cursor.execute("PRAGMA table_info(vocabulary_words)")
    }
    if "meaning" not in vocabulary_columns:
        cursor.execute(
            "ALTER TABLE vocabulary_words ADD COLUMN meaning TEXT"
        )

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vocabulary_word_forms(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        vocabulary_word_id INTEGER NOT NULL,
        grammatical_case TEXT NOT NULL,
        number TEXT NOT NULL CHECK(number IN ('singular', 'plural')),
        form TEXT NOT NULL,

        FOREIGN KEY(vocabulary_word_id)
            REFERENCES vocabulary_words(id)
            ON DELETE CASCADE,

        UNIQUE(vocabulary_word_id, grammatical_case, number, form)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vocabulary_paradigm_forms(

        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vocabulary_word_id INTEGER NOT NULL,
        part_of_speech TEXT NOT NULL,
        features TEXT NOT NULL,
        form TEXT NOT NULL,
        generation_method TEXT NOT NULL DEFAULT 'rule-based',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY(vocabulary_word_id)
            REFERENCES vocabulary_words(id)
            ON DELETE CASCADE,

        UNIQUE(vocabulary_word_id, part_of_speech, features, form)
    )
    """)

    # =========================
    # INDEXES
    # =========================

    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_articles_level
    ON articles(detected_level)
    """)

    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_articles_subject
    ON articles(subject)
    """)

    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_articles_exam_library
    ON articles(reuse_approved, subject)
    """)

    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_questions_article
    ON questions(article_id)
    """)

    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_exam_article
    ON exam_results(article_id)
    """)

    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_article_exam_category
    ON articles(reuse_approved, exam_category)
    """)

    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_answer_exam
    ON user_answers(exam_result_id)
    """)

    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_vocabulary_word_context
    ON vocabulary_words(word_key, article_id)
    """)

    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_vocabulary_forms_word
    ON vocabulary_word_forms(vocabulary_word_id, grammatical_case, number)
    """)

    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_vocabulary_paradigm_form
    ON vocabulary_paradigm_forms(form)
    """)

    conn.commit()
    conn.close()

    print(
        "Database initialized successfully."
    )


if __name__ == "__main__":
    init_db()