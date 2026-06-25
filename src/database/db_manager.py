"""SQLite helpers for Encrypta."""

import sqlite3

from ..config import DB_PATH
from .schema import initialize_database


def get_connection():
    initialize_database()
    return sqlite3.connect(DB_PATH)


def generate_user_id():
    initialize_database()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM User")
    user_ids = [row[0] for row in cursor.fetchall()]
    conn.close()
    return max(user_ids) + 1 if user_ids else 1
