import sqlite3

import pytest

from backend.database import db
from backend.database import init_db as database_init
from backend.repositories import article_ingestion_repository, article_repository, exam_result_repository, question_repository, user_answer_repository
from backend.repositories import (
    vocabulary_repository,
)


@pytest.fixture
def database(tmp_path, monkeypatch):
    database_path = tmp_path / "test_yki.db"

    def connect():
        connection = sqlite3.connect(database_path)
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    monkeypatch.setattr(db, "get_connection", connect)
    monkeypatch.setattr(database_init, "get_connection", connect)
    monkeypatch.setattr(article_repository, "get_connection", connect)
    monkeypatch.setattr(article_ingestion_repository, "get_connection", connect)
    monkeypatch.setattr(question_repository, "get_connection", connect)
    monkeypatch.setattr(exam_result_repository, "get_connection", connect)
    monkeypatch.setattr(user_answer_repository, "get_connection", connect)
    monkeypatch.setattr(vocabulary_repository, "get_connection", connect)

    database_init.init_db()
    return connect


@pytest.fixture(autouse=True)
def disable_fragment_autorefresh_in_tests(monkeypatch):
    import streamlit as st

    monkeypatch.setattr(
        st,
        "fragment",
        lambda **kwargs: lambda function: function
    )
