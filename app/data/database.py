import sqlite3
import json
from datetime import datetime
from typing import Optional
from app.data.models import Classification, Feedback

DB_PATH = "data/feedback.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS classifications (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            text        TEXT NOT NULL,
            category_id TEXT NOT NULL,
            category_name TEXT NOT NULL,
            confidence  REAL NOT NULL,
            reasoning   TEXT,
            key_factors TEXT,
            alternative_category TEXT,
            alternative_category_name TEXT,
            needs_review INTEGER DEFAULT 0,
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS feedback (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            classif_id      INTEGER REFERENCES classifications(id),
            feedback_type   TEXT NOT NULL,
            correct_label   TEXT,
            used_for_fewshot INTEGER DEFAULT 0,
            created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()


def save_classification(c: Classification) -> int:
    conn = get_connection()
    cursor = conn.execute("""
        INSERT INTO classifications
        (text, category_id, category_name, confidence, reasoning,
         key_factors, alternative_category, alternative_category_name, needs_review)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        c.text, c.category_id, c.category_name, c.confidence,
        c.reasoning, json.dumps(c.key_factors),
        c.alternative_category, c.alternative_category_name,
        int(c.needs_review)
    ))
    conn.commit()
    classif_id = cursor.lastrowid
    conn.close()
    return classif_id


def save_feedback(classif_id: int, feedback_type: str, correct_label: Optional[str]):
    conn = get_connection()
    conn.execute("""
        INSERT INTO feedback (classif_id, feedback_type, correct_label)
        VALUES (?, ?, ?)
    """, (classif_id, feedback_type, correct_label))
    conn.commit()
    conn.close()


def get_history(limit: int = 50) -> list:
    conn = get_connection()
    rows = conn.execute("""
        SELECT c.*, f.feedback_type, f.correct_label
        FROM classifications c
        LEFT JOIN feedback f ON f.classif_id = c.id
        ORDER BY c.created_at DESC
        LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_unused_wrong_feedbacks() -> list:
    conn = get_connection()
    rows = conn.execute("""
        SELECT f.id, f.correct_label, c.text
        FROM feedback f
        JOIN classifications c ON f.classif_id = c.id
        WHERE f.feedback_type = 'WRONG'
        AND f.used_for_fewshot = 0
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def count_unused_wrong_feedbacks() -> int:
    conn = get_connection()
    count = conn.execute("""
        SELECT COUNT(*) FROM feedback
        WHERE feedback_type = 'WRONG'
        AND used_for_fewshot = 0
    """).fetchone()[0]
    conn.close()
    return count


def mark_feedbacks_used(feedback_ids: list):
    conn = get_connection()
    conn.execute(f"""
        UPDATE feedback SET used_for_fewshot = 1
        WHERE id IN ({','.join('?' * len(feedback_ids))})
    """, feedback_ids)
    conn.commit()
    conn.close()
