
import sqlite3
from pathlib import Path

# Keep the database in the project folder.
DB_PATH = Path(__file__).parent / "interview_history.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    """Create the interview history table if it doesn't exist."""
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS interviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                feedback TEXT NOT NULL,
                score REAL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)


def save_interview(category, question, answer, feedback, score=None):
    """Save one completed interview review."""
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO interviews
                (category, question, answer, feedback, score)
            VALUES (?, ?, ?, ?, ?)
            """,
            (category, question, answer, feedback, score)
        )


def get_history():
    """Return saved interviews, newest first."""
    with get_connection() as connection:
        rows = connection.execute("""
            SELECT id, category, question, answer,
                   feedback, score, created_at
            FROM interviews
            ORDER BY id DESC
        """).fetchall()

    return rows


def delete_interview(interview_id):
    """Delete one saved interview by its ID."""
    with get_connection() as connection:
        connection.execute(
            "DELETE FROM interviews WHERE id = ?",
            (interview_id,)
        )
