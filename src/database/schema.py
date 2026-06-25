"""Database schema creation for the local SQLite database."""

import sqlite3
from pathlib import Path

from ..config import DB_PATH


SCHEMA_STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS User (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        password_hash TEXT,
        email TEXT,
        role TEXT,
        status TEXT,
        private_key TEXT,
        public_key TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS Messages (
        message_id INTEGER PRIMARY KEY,
        sender_id INTEGER,
        receiver_id INTEGER,
        content TEXT,
        encrypted_content TEXT,
        timestamp TEXT,
        is_encrypted BOOLEAN,
        plain_content TEXT,
        FOREIGN KEY (sender_id) REFERENCES User(user_id),
        FOREIGN KEY (receiver_id) REFERENCES User(user_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS DirectMessages (
        direct_message_id INTEGER PRIMARY KEY,
        message_id INTEGER,
        receiver_id INTEGER,
        message TEXT,
        encryption_type TEXT,
        FOREIGN KEY (message_id) REFERENCES Messages(message_id),
        FOREIGN KEY (receiver_id) REFERENCES User(user_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS "Group" (
        group_id INTEGER PRIMARY KEY,
        group_name TEXT,
        group_size INTEGER,
        symmetric_key TEXT,
        creator_id INTEGER,
        creator TEXT,
        FOREIGN KEY (creator_id) REFERENCES User(user_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS GroupMessages (
        group_message_id INTEGER PRIMARY KEY,
        group_id INTEGER,
        message_id INTEGER,
        message_content TEXT,
        timestamp TEXT,
        encryption_type TEXT,
        sender_id INTEGER,
        FOREIGN KEY (group_id) REFERENCES "Group"(group_id),
        FOREIGN KEY (message_id) REFERENCES Messages(message_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS GroupMembership (
        group_membership_id INTEGER PRIMARY KEY,
        group_id INTEGER,
        user_id INTEGER,
        FOREIGN KEY (group_id) REFERENCES "Group"(group_id),
        FOREIGN KEY (user_id) REFERENCES User(user_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS Connection (
        username TEXT,
        connection_id INTEGER PRIMARY KEY,
        sender_id INTEGER,
        receiver_id INTEGER,
        status TEXT,
        connection_ip_address TEXT,
        timestamp TEXT,
        FOREIGN KEY (sender_id) REFERENCES User(user_id),
        FOREIGN KEY (receiver_id) REFERENCES User(user_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS Call (
        call_id INTEGER PRIMARY KEY,
        caller_id INTEGER,
        receiver_id INTEGER,
        start_time TEXT,
        end_time TEXT,
        duration TEXT,
        type TEXT,
        FOREIGN KEY (caller_id) REFERENCES User(user_id),
        FOREIGN KEY (receiver_id) REFERENCES User(user_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS GroupKeys (
        key_id INTEGER PRIMARY KEY,
        group_id INTEGER,
        user_id INTEGER,
        encrypted_key BLOB,
        FOREIGN KEY (group_id) REFERENCES "Group"(group_id),
        FOREIGN KEY (user_id) REFERENCES User(user_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS Authentication (
        auth_id INTEGER PRIMARY KEY,
        user_id INTEGER,
        password_hash TEXT,
        twofa_code TEXT,
        twofa_expiration INTEGER,
        FOREIGN KEY (user_id) REFERENCES User(user_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS Notifications (
        noti_id INTEGER PRIMARY KEY,
        user_id INTEGER,
        related_entity_id INTEGER,
        noti_type TEXT,
        status TEXT,
        FOREIGN KEY (user_id) REFERENCES User(user_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS Session (
        session_id INTEGER PRIMARY KEY,
        user_id INTEGER,
        login_time TEXT,
        logout_time TEXT,
        session_token TEXT,
        ip_address TEXT,
        FOREIGN KEY (user_id) REFERENCES User(user_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS Files (
        file_id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id INTEGER NOT NULL,
        receiver_id INTEGER NOT NULL,
        filename TEXT NOT NULL,
        content TEXT NOT NULL,
        timestamp DATETIME NOT NULL,
        FOREIGN KEY (sender_id) REFERENCES User(user_id),
        FOREIGN KEY (receiver_id) REFERENCES User(user_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS GroupMemberConnections (
        number_id INTEGER,
        group_id INTEGER,
        member_id INTEGER,
        member_ip TEXT,
        username TEXT,
        FOREIGN KEY (member_id) REFERENCES User(user_id),
        PRIMARY KEY (number_id)
    )
    """,
]


def initialize_database(db_path: str | Path = DB_PATH) -> Path:
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        for statement in SCHEMA_STATEMENTS:
            cursor.execute(statement)
        conn.commit()
    finally:
        conn.close()
    return db_path
