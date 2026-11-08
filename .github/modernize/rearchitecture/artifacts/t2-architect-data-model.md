# Existing SQLite Data Model

Schema is created by `database/init_db.py`; `database.db.get_connection()` opens `data/yki.db`, enables foreign keys, and returns a raw connection. Models are Python dataclasses, not ORM entities. This inventory does not read or inspect the database file.

## Tables and fields

- **`articles`** — `id`, `title`, `source`, `content`, `detected_level`, `level_confidence`, `subject`, `subject_confidence`, `word_count`, `status`, `reuse_approved`, `rights_basis`, `permission_reference`, `reuse_approved_by`, `reuse_approved_at`, `exam_category`, `created_at`.
- **`article_ingestion_sources`** — `id`, `publisher`, `feed_url` (unique), `rights_basis`, `permission_reference`, `approved_by`, `exam_category`, `active`, `created_at`, `last_checked_at`.
- **`questions`** — `id`, `article_id`, `question_no`, `question_type`, `question`, `option_a`–`option_d`, `correct_answer`, `keywords`, `explanation`.
- **`exam_results`** — `id`, `article_id`, `correct_answers`, `total_questions`, `score`, `created_at`.
- **`exam_result_articles`** — `exam_result_id`, `article_id`, `article_order`; composite primary key `(exam_result_id, article_id)`.
- **`user_answers`** — `id`, `exam_result_id`, `question_id`, `selected_answer`, `is_correct`, `created_at`.
- **`vocabulary_translations`** — `id`, `phrase_key`, `phrase`, `source_language`, `target_language`, `translation`, `provider`, `created_at`, `updated_at`; unique `(phrase_key, source_language, target_language)`.
- **`vocabulary_words`** — `id`, `word_key`, `word_form`, `lemma`, `part_of_speech`, `meaning`, `noun_type`, `verb_type`, JSON-text fields `suffixes`, `grammatical_features`, `stem_changes`, `subject`, `article_id`, `created_at`, `updated_at`.
- **`vocabulary_word_forms`** — `id`, `vocabulary_word_id`, `grammatical_case`, `number`, `form`; `number` constrained to singular/plural; unique word/case/number/form.
- **`vocabulary_paradigm_forms`** — `id`, `vocabulary_word_id`, `part_of_speech`, `features`, `form`, `generation_method`, `created_at`; unique word/part-of-speech/features/form.

## Relationships and ownership implications

- `questions.article_id` → `articles.id`.
- `exam_results.article_id` → `articles.id`.
- `exam_result_articles.exam_result_id` → `exam_results.id` with delete cascade; `article_id` → `articles.id`. It preserves ordered membership for multi-article exams alongside the required singular `exam_results.article_id`.
- `user_answers.exam_result_id` → `exam_results.id`; `question_id` → `questions.id`.
- `vocabulary_words.article_id` → `articles.id` (nullable).
- `vocabulary_word_forms.vocabulary_word_id` and `vocabulary_paradigm_forms.vocabulary_word_id` → `vocabulary_words.id`, both with delete cascade.
- Feed-source records are independent records; article `source` stores the imported article URL and is checked for duplicates.
- There are no user/identity or billing tables in the current schema.

## Important storage behavior

- Only approved articles (`reuse_approved = 1`) with the configured question distribution are eligible for random sample exams.
- Reuse provenance is stored on the article record; feed sources separately retain publisher, license/permission reference, approver, active status, category and last-check time.
- User-submitted reading content uses session-only UI state and is not saved as an approved library article. Scoring persists results only when `article_id` is present and all questions have stored IDs; otherwise the result remains in the session response.
- Vocabulary translations and tutor analyses are cached in SQLite; this is distinct from storing the entire user article.
- `init_db()` creates tables/indexes and adds selected missing columns (`articles`, `article_ingestion_sources`, `vocabulary_words`) before committing. This is a startup write and must be directed to an isolated temp DB in tests.
- Repository calls generally open/close a connection and commit independently. Article plus generated questions, and exam result plus user answers, do not show one shared unit-of-work transaction across repository methods.

## Upstream Artifacts Consumed

- `.github/modernize/rearchitecture/artifacts/t1-teamlead.md` — required user-data, consent and library/user-text preservation.
- `.github/modernize/rearchitecture/clarification.md` — SQLite adapter and do-not-touch database constraint.
- `database/init_db.py`, `database/db.py`, and repository SQL — schema/relationship evidence; `data/yki.db` was not opened.

## Evidence Mapping

- `database/init_db.py:14-341` → table/column inventory and schema initialization.
- `database/db.py:1-9` → connection path and foreign-key enforcement.
- `repositories/article_repository.py:27-104` and `:107-207` → rights-approved writes and example eligibility.
- `services/score_service.py:24-108`, `repositories/exam_result_repository.py`, `repositories/user_answer_repository.py` → conditional persistence and independent writes.
- `t1-teamlead.md#IV` → data-protection constraints.
