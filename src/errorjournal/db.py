import os
import sqlite3
from pathlib import Path
from contextlib import closing

def get_db_path() -> Path:
    """Returns the database file path, which allows for env overrides"""
    env_path = os.environ.get("EJ_DB")
    if env_path:
        db_path = Path(env_path)
    else:
        db_path = Path.home() / ".errorjournal" / "journal.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return db_path

def get_connection() -> sqlite3.Connection:
    """Creates the DB and tables if missing and returns a connection"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)

    conn.row_factory = sqlite3.Row

    conn.execute("""
            CREATE TABLE IF NOT EXISTS runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                started_at TEXT NOT NULL,
                command TEXT NOT NULL,
                target_file TEXT,
                exit_code INTEGER NOT NULL,
                duration_ms INTEGER NOT NULL,
                stderr TEXT
            )
        """)
    conn.commit()
    return conn

def insert_run(started_at: str, command: str, target_file: str | None, exit_code: int, duration_ms: int, stderr: str) -> None:
    """Inserts a record into SQLite"""
    query = """INSERT INTO runs(started_at, command, target_file, exit_code, duration_ms, stderr)
    VALUES (?, ?, ?, ?, ?, ?)"""
    conn = get_connection()
    with closing(conn), conn:
        conn.execute(query, (started_at, command, target_file, exit_code, duration_ms, stderr))

def recent_runs(limit: int) -> list[sqlite3.Row]:
    """Gets the most recent runs from the database"""
    query = "SELECT id, started_at, command, exit_code, duration_ms FROM runs ORDER BY id DESC LIMIT ?"
    conn = get_connection()
    with closing(conn):
        return conn.execute(query, (limit,)).fetchall()