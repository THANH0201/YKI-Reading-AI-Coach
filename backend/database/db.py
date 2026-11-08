# from database.db import get_connection every where in project

import sqlite3


def get_connection():

    conn = sqlite3.connect("data/yki.db")

    conn.execute("PRAGMA foreign_keys = ON")

    return conn
