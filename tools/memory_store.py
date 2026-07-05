import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = ROOT_DIR / "langlearn_memory.sqlite3"


def db_path():
    return Path(os.getenv("LANGLEARN_DB_PATH", DEFAULT_DB_PATH))


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def connect():
    path = db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    ensure_schema(conn)
    return conn


def ensure_schema(conn):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS phrase_progress (
            student_id TEXT NOT NULL,
            phrase TEXT NOT NULL,
            status TEXT NOT NULL,
            mistake_type TEXT DEFAULT 'none',
            attempts INTEGER NOT NULL DEFAULT 0,
            correct_attempts INTEGER NOT NULL DEFAULT 0,
            last_feedback TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            PRIMARY KEY (student_id, phrase)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS progress_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            phrase TEXT NOT NULL,
            status TEXT NOT NULL,
            mistake_type TEXT DEFAULT 'none',
            feedback TEXT,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()


def upsert_progress(student_id, phrase, status, mistake_type="none", feedback=None):
    now = utc_now()
    with connect() as conn:
        existing = conn.execute(
            """
            SELECT attempts, correct_attempts
            FROM phrase_progress
            WHERE student_id = ? AND phrase = ?
            """,
            (student_id, phrase),
        ).fetchone()
        attempts = (existing["attempts"] if existing else 0) + 1
        correct_attempts = (existing["correct_attempts"] if existing else 0) + (
            1 if status == "learned" else 0
        )

        conn.execute(
            """
            INSERT INTO phrase_progress (
                student_id, phrase, status, mistake_type, attempts,
                correct_attempts, last_feedback, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(student_id, phrase) DO UPDATE SET
                status = excluded.status,
                mistake_type = excluded.mistake_type,
                attempts = excluded.attempts,
                correct_attempts = excluded.correct_attempts,
                last_feedback = excluded.last_feedback,
                updated_at = excluded.updated_at
            """,
            (
                student_id,
                phrase,
                status,
                mistake_type,
                attempts,
                correct_attempts,
                feedback,
                now,
                now,
            ),
        )
        conn.execute(
            """
            INSERT INTO progress_events (
                student_id, phrase, status, mistake_type, feedback, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (student_id, phrase, status, mistake_type, feedback, now),
        )
        conn.commit()
        return get_memory_snapshot(student_id)


def get_memory_snapshot(student_id):
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT phrase, status, mistake_type, attempts, correct_attempts,
                   last_feedback, updated_at
            FROM phrase_progress
            WHERE student_id = ?
            ORDER BY updated_at DESC
            """,
            (student_id,),
        ).fetchall()

    learned = [row["phrase"] for row in rows if row["status"] == "learned"]
    needs_review = [row["phrase"] for row in rows if row["status"] == "needs_review"]
    not_learned = [row["phrase"] for row in rows if row["status"] == "not_learned"]
    weak_areas = sorted(
        {
            row["mistake_type"]
            for row in rows
            if row["mistake_type"] and row["mistake_type"] != "none"
        }
    )

    if len(learned) >= 12:
        level = "intermediate"
    elif len(learned) >= 4:
        level = "early_beginner"
    else:
        level = "beginner"

    return {
        "student_id": student_id,
        "level": level,
        "learned_phrases": learned,
        "needs_review": needs_review,
        "not_learned": not_learned,
        "weak_areas": weak_areas,
        "phrase_count": len(rows),
        "phrases": [dict(row) for row in rows],
        "db_path": str(db_path()),
    }
