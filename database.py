"""SQLite persistence for transactions."""
import sqlite3
from pathlib import Path


def init_db(path: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS transactions (
            transaction_id TEXT PRIMARY KEY, amount REAL NOT NULL,
            location TEXT NOT NULL, transaction_type TEXT NOT NULL,
            risk_score INTEGER NOT NULL, status TEXT NOT NULL, created_at TEXT NOT NULL
        )""")


def connect(path: str):
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def as_dict(row):
    return dict(row) if row else None
