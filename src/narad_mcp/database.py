import sqlite3
import json
from datetime import datetime
from pathlib import Path

DB_PATH = Path("narad_agent.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize all tables on first run."""
    conn = get_connection()
    cursor = conn.cursor()

    # --- Conversation Memory ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversation_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,         -- 'user' or 'assistant'
            message TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)

    # --- PR Review Log ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pr_reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            repo TEXT NOT NULL,
            pr_number INTEGER NOT NULL,
            pr_title TEXT,
            review TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)

    # --- Daily Digest Log ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_digests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            digest TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()

# ─── Conversation Memory ────────────────────────────────────────────────────

def save_message(session_id: str, role: str, message: str):
    conn = get_connection()
    conn.execute(
        "INSERT INTO conversation_history (session_id, role, message, timestamp) VALUES (?, ?, ?, ?)",
        (session_id, role, message, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

def get_recent_history(session_id: str, limit: int = 10) -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT role, message FROM conversation_history WHERE session_id = ? ORDER BY id DESC LIMIT ?",
        (session_id, limit)
    ).fetchall()
    conn.close()
    return [{"role": row["role"], "message": row["message"]} for row in reversed(rows)]

# ─── PR Review Log ──────────────────────────────────────────────────────────

def save_pr_review(repo: str, pr_number: int, pr_title: str, review: str):
    conn = get_connection()
    conn.execute(
        "INSERT INTO pr_reviews (repo, pr_number, pr_title, review, timestamp) VALUES (?, ?, ?, ?, ?)",
        (repo, pr_number, pr_title, review, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

def get_past_pr_reviews(repo: str) -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT pr_number, pr_title, review, timestamp FROM pr_reviews WHERE repo = ? ORDER BY id DESC LIMIT 5",
        (repo,)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]

# ─── Daily Digest Log ───────────────────────────────────────────────────────

def save_digest(digest: str):
    conn = get_connection()
    conn.execute(
        "INSERT INTO daily_digests (digest, timestamp) VALUES (?, ?)",
        (digest, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

def get_last_digest() -> dict | None:
    conn = get_connection()
    row = conn.execute(
        "SELECT digest, timestamp FROM daily_digests ORDER BY id DESC LIMIT 1"
    ).fetchone()
    conn.close()
    return dict(row) if row else None
