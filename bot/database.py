import sqlite3
from pathlib import Path
from contextlib import contextmanager

DB_PATH = Path(__file__).parent.parent / "data.db"


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS distributors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE NOT NULL,
                full_name TEXT,
                language TEXT DEFAULT 'uz',
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                distributor_id INTEGER NOT NULL,
                shop_name TEXT NOT NULL,
                address_text TEXT,
                latitude REAL,
                longitude REAL,
                phone TEXT,
                product_name TEXT,
                quantity TEXT,
                photo_path TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (distributor_id) REFERENCES distributors(id)
            )
        """)


def get_distributor(telegram_id: int):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM distributors WHERE telegram_id = ?", (telegram_id,)
        ).fetchone()
        return dict(row) if row else None


def create_distributor(telegram_id: int, full_name: str, language: str):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO distributors (telegram_id, full_name, language) VALUES (?, ?, ?)",
            (telegram_id, full_name, language),
        )


def set_language(telegram_id: int, language: str):
    with get_conn() as conn:
        conn.execute(
            "UPDATE distributors SET language = ? WHERE telegram_id = ?",
            (language, telegram_id),
        )
