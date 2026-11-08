from contextlib import closing
from pathlib import Path
import runpy


def test_database_initialization_is_idempotent_and_creates_workflow_tables(database):
    from database.init_db import init_db

    init_db()
    with closing(database()) as connection:
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }

    assert {
        "articles",
        "article_ingestion_sources",
        "exam_result_articles",
        "questions",
        "exam_results",
        "user_answers",
        "vocabulary_translations",
        "vocabulary_words",
        "vocabulary_word_forms"
    }.issubset(tables)
    with closing(database()) as connection:
        vocabulary_columns = {
            row[1]
            for row in connection.execute(
                "PRAGMA table_info(vocabulary_words)"
            )
        }
    assert "meaning" in vocabulary_columns
    with closing(database()) as connection:
        article_columns = {
            row[1]
            for row in connection.execute("PRAGMA table_info(articles)")
        }
        source_columns = {
            row[1]
            for row in connection.execute(
                "PRAGMA table_info(article_ingestion_sources)"
            )
        }
    assert "exam_category" in article_columns
    assert "exam_category" in source_columns


def test_database_connection_enables_foreign_keys(database):
    with closing(database()) as connection:
        assert connection.execute("PRAGMA foreign_keys").fetchone()[0] == 1


def test_get_connection_enables_foreign_keys(monkeypatch):
    import database.db as database_module

    connection = __import__("sqlite3").connect(":memory:")
    monkeypatch.setattr(database_module.sqlite3, "connect", lambda path: connection)

    assert database_module.get_connection() is connection
    assert connection.execute("PRAGMA foreign_keys").fetchone()[0] == 1
    connection.close()


def test_database_init_script_entrypoint_uses_initializer(database, monkeypatch, capsys):
    import database.db as database_module

    monkeypatch.setattr(database_module, "get_connection", database)
    script_path = Path(__file__).resolve().parents[1] / "database" / "init_db.py"
    runpy.run_path(str(script_path), run_name="__main__")

    assert "Database initialized successfully." in capsys.readouterr().out
