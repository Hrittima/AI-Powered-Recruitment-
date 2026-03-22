import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "resumes.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS resumes (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            name    TEXT,
            score   INTEGER,
            matched TEXT,
            rank    TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

# FIX: now accepts matched as a list and stores as comma-separated string
def save_resume(name, score, matched, rank):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    matched_str = ", ".join(matched) if isinstance(matched, list) else str(matched)
    cur.execute(
        "INSERT INTO resumes (name, score, matched, rank) VALUES (?, ?, ?, ?)",
        (name, score, matched_str, rank)
    )
    conn.commit()
    conn.close()

def get_all_resumes():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT name, score, matched, rank, created_at FROM resumes ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return [
        {"name": r[0], "score": r[1], "matched": r[2], "rank": r[3], "date": r[4]}
        for r in rows
    ]