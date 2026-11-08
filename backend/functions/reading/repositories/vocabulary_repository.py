import json

from backend.database.db import get_connection


class VocabularyRepository:
    @staticmethod
    def _normalize_phrase(phrase: str) -> str:
        return " ".join(phrase.split()).casefold()

    @staticmethod
    def get_translation(
        phrase: str, source_language: str = "fi", target_language: str = "en"
    ) -> dict | None:
        phrase_key = VocabularyRepository._normalize_phrase(phrase)
        conn = get_connection()

        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT phrase, translation, provider
                FROM vocabulary_translations
                WHERE phrase_key = ?
                  AND source_language = ?
                  AND target_language = ?
            """,
                (phrase_key, source_language, target_language),
            )
            row = cursor.fetchone()
        finally:
            conn.close()

        if row is None:
            return None

        return {"phrase": row[0], "translation": row[1], "provider": row[2]}

    @staticmethod
    def save_translation(
        phrase: str,
        translation: str,
        provider: str = "MyMemory",
        source_language: str = "fi",
        target_language: str = "en",
    ) -> None:
        phrase_key = VocabularyRepository._normalize_phrase(phrase)
        normalized_phrase = " ".join(phrase.split())
        conn = get_connection()

        try:
            conn.execute(
                """
                INSERT INTO vocabulary_translations (
                    phrase_key,
                    phrase,
                    source_language,
                    target_language,
                    translation,
                    provider
                )
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(phrase_key, source_language, target_language)
                DO UPDATE SET
                    phrase = excluded.phrase,
                    translation = excluded.translation,
                    provider = excluded.provider,
                    updated_at = CURRENT_TIMESTAMP
            """,
                (
                    phrase_key,
                    normalized_phrase,
                    source_language,
                    target_language,
                    translation.strip(),
                    provider,
                ),
            )
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def save_word_analysis(
        word_form: str,
        lemma: str,
        part_of_speech: str,
        meaning: str | None = None,
        noun_type: str | None = None,
        verb_type: int | None = None,
        suffixes: list[dict[str, str]] | None = None,
        grammatical_features: dict[str, str] | None = None,
        stem_changes: list[str] | None = None,
        word_forms: list[dict[str, str]] | None = None,
        subject: str | None = None,
        article_id: int | None = None,
        paradigm_forms: list[dict] | None = None,
    ) -> dict:
        word_key = VocabularyRepository._normalize_phrase(lemma)
        normalized_word = " ".join(word_form.split())
        normalized_lemma = " ".join(lemma.split())
        conn = get_connection()

        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id
                FROM vocabulary_words
                WHERE word_key = ?
                  AND article_id IS ?
            """,
                (word_key, article_id),
            )
            row = cursor.fetchone()

            values = (
                normalized_word,
                normalized_lemma,
                part_of_speech.strip(),
                meaning.strip() if meaning else None,
                noun_type,
                verb_type,
                json.dumps(suffixes or [], ensure_ascii=False),
                json.dumps(grammatical_features or {}, ensure_ascii=False),
                json.dumps(stem_changes or [], ensure_ascii=False),
                subject,
                article_id,
            )

            if row is None:
                cursor.execute(
                    """
                    INSERT INTO vocabulary_words (
                        word_key,
                        word_form,
                        lemma,
                        part_of_speech,
                        meaning,
                        noun_type,
                        verb_type,
                        suffixes,
                        grammatical_features,
                        stem_changes,
                        subject,
                        article_id
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (word_key, *values),
                )
                word_id = cursor.lastrowid
            else:
                word_id = row[0]
                cursor.execute(
                    """
                    UPDATE vocabulary_words
                    SET word_form = ?,
                        lemma = ?,
                        part_of_speech = ?,
                        meaning = COALESCE(?, meaning),
                        noun_type = ?,
                        verb_type = ?,
                        suffixes = ?,
                        grammatical_features = ?,
                        stem_changes = ?,
                        subject = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """,
                    (*values[:10], word_id),
                )

            for form in word_forms or []:
                cursor.execute(
                    """
                    INSERT INTO vocabulary_word_forms (
                        vocabulary_word_id,
                        grammatical_case,
                        number,
                        form
                    )
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(
                        vocabulary_word_id,
                        grammatical_case,
                        number,
                        form
                    ) DO NOTHING
                """,
                    (
                        word_id,
                        form["grammatical_case"],
                        form["number"],
                        " ".join(form["form"].split()),
                    ),
                )

            for form in paradigm_forms or []:
                cursor.execute(
                    """
                    INSERT INTO vocabulary_paradigm_forms (
                        vocabulary_word_id,
                        part_of_speech,
                        features,
                        form,
                        generation_method
                    )
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(
                        vocabulary_word_id,
                        part_of_speech,
                        features,
                        form
                    ) DO NOTHING
                """,
                    (
                        word_id,
                        form["part_of_speech"],
                        json.dumps(
                            form["features"], ensure_ascii=False, sort_keys=True
                        ),
                        " ".join(form["form"].split()),
                        form.get("generation_method", "rule-based"),
                    ),
                )

            conn.commit()
        finally:
            conn.close()

        return {
            "id": word_id,
            "word_form": normalized_word,
            "lemma": normalized_lemma,
            "part_of_speech": part_of_speech.strip(),
            "meaning": meaning.strip() if meaning else None,
            "noun_type": noun_type,
            "verb_type": verb_type,
            "suffixes": suffixes or [],
            "grammatical_features": grammatical_features or {},
            "stem_changes": stem_changes or [],
            "forms": word_forms or [],
            "paradigm_forms": paradigm_forms or [],
            "subject": subject,
            "article_id": article_id,
        }

    @staticmethod
    def get_word_analysis(lemma: str, article_id: int | None = None) -> dict | None:
        word_key = VocabularyRepository._normalize_phrase(lemma)
        conn = get_connection()

        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id
                FROM vocabulary_words
                WHERE word_key = ?
                  AND article_id IS ?
            """,
                (word_key, article_id),
            )
            row = cursor.fetchone()
        finally:
            conn.close()

        if row is None:
            return None

        return VocabularyRepository.get_word_analysis_by_id(row[0])

    @staticmethod
    def get_word_analysis_for_form(
        word_form: str, article_id: int | None = None
    ) -> dict | None:
        word_key = VocabularyRepository._normalize_phrase(word_form)
        conn = get_connection()

        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id
                FROM vocabulary_words
                WHERE word_key = ?
                   OR lower(word_form) = lower(?)
                   OR EXISTS (
                       SELECT 1
                       FROM vocabulary_word_forms
                       WHERE vocabulary_word_forms.vocabulary_word_id =
                           vocabulary_words.id
                         AND lower(vocabulary_word_forms.form) = lower(?)
                   )
                   OR EXISTS (
                         SELECT 1
                         FROM vocabulary_paradigm_forms
                         WHERE vocabulary_paradigm_forms.vocabulary_word_id =
                             vocabulary_words.id
                           AND lower(vocabulary_paradigm_forms.form) = lower(?)
                   )
                ORDER BY
                    CASE
                        WHEN article_id IS ? THEN 0
                        WHEN article_id IS NULL THEN 1
                        ELSE 2
                    END,
                    updated_at DESC
                LIMIT 1
            """,
                (
                    word_key,
                    " ".join(word_form.split()),
                    " ".join(word_form.split()),
                    " ".join(word_form.split()),
                    article_id,
                ),
            )
            row = cursor.fetchone()
        finally:
            conn.close()

        if row is None:
            return None

        return VocabularyRepository.get_word_analysis_by_id(row[0])

    @staticmethod
    def get_word_analysis_by_id(word_id: int) -> dict | None:
        conn = get_connection()

        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT
                    id,
                    word_form,
                    lemma,
                    part_of_speech,
                    meaning,
                    noun_type,
                    verb_type,
                    suffixes,
                    grammatical_features,
                    stem_changes,
                    subject,
                    article_id
                FROM vocabulary_words
                WHERE id = ?
            """,
                (word_id,),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            cursor.execute(
                """
                SELECT grammatical_case, number, form
                FROM vocabulary_word_forms
                WHERE vocabulary_word_id = ?
                ORDER BY grammatical_case, number, form
            """,
                (word_id,),
            )
            forms = [
                {"grammatical_case": form[0], "number": form[1], "form": form[2]}
                for form in cursor.fetchall()
            ]
            cursor.execute(
                """
                SELECT part_of_speech, features, form, generation_method
                FROM vocabulary_paradigm_forms
                WHERE vocabulary_word_id = ?
                ORDER BY part_of_speech, form, features
            """,
                (word_id,),
            )
            paradigm_forms = [
                {
                    "part_of_speech": form[0],
                    "features": json.loads(form[1]),
                    "form": form[2],
                    "generation_method": form[3],
                }
                for form in cursor.fetchall()
            ]
        finally:
            conn.close()

        return {
            "id": row[0],
            "word_form": row[1],
            "lemma": row[2],
            "part_of_speech": row[3],
            "meaning": row[4],
            "noun_type": row[5],
            "verb_type": row[6],
            "suffixes": json.loads(row[7]),
            "grammatical_features": json.loads(row[8]),
            "stem_changes": json.loads(row[9]),
            "forms": forms,
            "paradigm_forms": paradigm_forms,
            "subject": row[10],
            "article_id": row[11],
        }
