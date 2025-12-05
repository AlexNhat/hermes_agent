# db.py
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional

DB_PATH = Path("hermes_logs.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db() -> None:
    """
    Khởi tạo database và bảng lưu lịch sử chat nếu chưa có.
    """
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS chat_interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            user_message TEXT NOT NULL,
            assistant_message TEXT NOT NULL,
            user_timestamp TEXT NOT NULL,
            assistant_timestamp TEXT NOT NULL,
            response_time_ms REAL NOT NULL,
            model_name TEXT
        );
        """
    )
    conn.commit()
    conn.close()


def insert_interaction(
    user_id: str,
    user_message: str,
    assistant_message: str,
    user_timestamp: str,
    assistant_timestamp: str,
    response_time_ms: float,
    model_name: Optional[str] = None,
) -> None:
    """
    Lưu một lượt tương tác (Q&A) vào database.
    """
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO chat_interactions (
            user_id,
            user_message,
            assistant_message,
            user_timestamp,
            assistant_timestamp,
            response_time_ms,
            model_name
        )
        VALUES (?, ?, ?, ?, ?, ?, ?);
        """,
        (
            user_id,
            user_message,
            assistant_message,
            user_timestamp,
            assistant_timestamp,
            response_time_ms,
            model_name,
        ),
    )
    conn.commit()
    conn.close()
