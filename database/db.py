# from database.db import get_connection every where in project

import sqlite3

DB_PATH = "data/yki.db"

def get_connection():
    return sqlite3.connect(DB_PATH)
