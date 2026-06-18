from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

DEFAULT_DB_PATH = Path(__file__).resolve().parents[1] / "data" / "app.db"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _resolve_db_path(db_path: Optional[str] = None) -> Path:
    path = Path(db_path) if db_path else DEFAULT_DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def get_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    conn = sqlite3.connect(_resolve_db_path(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Optional[str] = None) -> None:
    with get_connection(db_path) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS datasets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                row_count INTEGER NOT NULL DEFAULT 0,
                column_count INTEGER NOT NULL DEFAULT 0,
                uploaded_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS analysis_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                dataset_id INTEGER NOT NULL,
                summary_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (dataset_id) REFERENCES datasets(id)
            );

            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT NOT NULL,
                details TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
            """
        )


def user_count(db_path: Optional[str] = None) -> int:
    with get_connection(db_path) as conn:
        row = conn.execute("SELECT COUNT(*) AS cnt FROM users").fetchone()
        return int(row["cnt"])


def create_user(
    username: str,
    email: str,
    password_hash: str,
    salt: str,
    role: str,
    db_path: Optional[str] = None,
) -> int:
    now = _utc_now()
    with get_connection(db_path) as conn:
        cursor = conn.execute(
            """
            INSERT INTO users (username, email, password_hash, salt, role, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (username, email, password_hash, salt, role, now, now),
        )
        return int(cursor.lastrowid)


def _row_to_dict(row: Optional[sqlite3.Row]) -> Optional[Dict[str, Any]]:
    return dict(row) if row else None


def get_user_by_username(username: str, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    with get_connection(db_path) as conn:
        row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    return _row_to_dict(row)


def get_user_by_email(email: str, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    with get_connection(db_path) as conn:
        row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    return _row_to_dict(row)


def get_user_by_id(user_id: int, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    with get_connection(db_path) as conn:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    return _row_to_dict(row)


def list_users(db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    with get_connection(db_path) as conn:
        rows = conn.execute(
            "SELECT id, username, email, role, created_at, updated_at FROM users ORDER BY id"
        ).fetchall()
    return [dict(r) for r in rows]


def update_password(username: str, password_hash: str, salt: str, db_path: Optional[str] = None) -> bool:
    now = _utc_now()
    with get_connection(db_path) as conn:
        cursor = conn.execute(
            """
            UPDATE users
            SET password_hash = ?, salt = ?, updated_at = ?
            WHERE username = ?
            """,
            (password_hash, salt, now, username),
        )
    return cursor.rowcount > 0


def create_dataset(
    user_id: int,
    name: str,
    file_path: str,
    row_count: int,
    column_count: int,
    db_path: Optional[str] = None,
) -> int:
    now = _utc_now()
    with get_connection(db_path) as conn:
        cursor = conn.execute(
            """
            INSERT INTO datasets (user_id, name, file_path, row_count, column_count, uploaded_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user_id, name, file_path, row_count, column_count, now),
        )
        return int(cursor.lastrowid)


def list_datasets_for_user(
    user_id: int,
    role: str,
    db_path: Optional[str] = None,
) -> List[Dict[str, Any]]:
    query = (
        """
        SELECT d.id, d.user_id, u.username, d.name, d.file_path, d.row_count, d.column_count, d.uploaded_at
        FROM datasets d
        JOIN users u ON u.id = d.user_id
        """
    )
    params: tuple[Any, ...] = ()
    if role != "admin":
        query += " WHERE d.user_id = ?"
        params = (user_id,)
    query += " ORDER BY d.uploaded_at DESC"

    with get_connection(db_path) as conn:
        rows = conn.execute(query, params).fetchall()
    return [dict(r) for r in rows]


def get_dataset_for_user(
    dataset_id: int,
    user_id: int,
    role: str,
    db_path: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    if role == "admin":
        query = (
            """
            SELECT d.id, d.user_id, u.username, d.name, d.file_path, d.row_count, d.column_count, d.uploaded_at
            FROM datasets d
            JOIN users u ON u.id = d.user_id
            WHERE d.id = ?
            """
        )
        params: tuple[Any, ...] = (dataset_id,)
    else:
        query = (
            """
            SELECT d.id, d.user_id, u.username, d.name, d.file_path, d.row_count, d.column_count, d.uploaded_at
            FROM datasets d
            JOIN users u ON u.id = d.user_id
            WHERE d.id = ? AND d.user_id = ?
            """
        )
        params = (dataset_id, user_id)

    with get_connection(db_path) as conn:
        row = conn.execute(query, params).fetchone()
    return _row_to_dict(row)


def save_analysis_run(
    user_id: int,
    dataset_id: int,
    summary: Dict[str, Any],
    db_path: Optional[str] = None,
) -> int:
    now = _utc_now()
    with get_connection(db_path) as conn:
        cursor = conn.execute(
            """
            INSERT INTO analysis_runs (user_id, dataset_id, summary_json, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, dataset_id, json.dumps(summary), now),
        )
        return int(cursor.lastrowid)


def list_analysis_runs(
    user_id: int,
    role: str,
    db_path: Optional[str] = None,
) -> List[Dict[str, Any]]:
    query = (
        """
        SELECT ar.id, ar.user_id, u.username, ar.dataset_id, d.name AS dataset_name, ar.summary_json, ar.created_at
        FROM analysis_runs ar
        JOIN users u ON u.id = ar.user_id
        JOIN datasets d ON d.id = ar.dataset_id
        """
    )
    params: tuple[Any, ...] = ()
    if role != "admin":
        query += " WHERE ar.user_id = ?"
        params = (user_id,)
    query += " ORDER BY ar.created_at DESC"

    with get_connection(db_path) as conn:
        rows = conn.execute(query, params).fetchall()
    return [dict(r) for r in rows]


def log_audit_event(
    action: str,
    user_id: Optional[int] = None,
    details: Optional[str] = None,
    db_path: Optional[str] = None,
) -> int:
    now = _utc_now()
    with get_connection(db_path) as conn:
        cursor = conn.execute(
            "INSERT INTO audit_logs (user_id, action, details, created_at) VALUES (?, ?, ?, ?)",
            (user_id, action, details, now),
        )
        return int(cursor.lastrowid)


def list_audit_logs(
    user_id: int,
    role: str,
    db_path: Optional[str] = None,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    if role == "admin":
        query = (
            """
            SELECT a.id, a.user_id, u.username, a.action, a.details, a.created_at
            FROM audit_logs a
            LEFT JOIN users u ON u.id = a.user_id
            ORDER BY a.created_at DESC
            LIMIT ?
            """
        )
        params: tuple[Any, ...] = (limit,)
    else:
        query = (
            """
            SELECT a.id, a.user_id, u.username, a.action, a.details, a.created_at
            FROM audit_logs a
            LEFT JOIN users u ON u.id = a.user_id
            WHERE a.user_id = ?
            ORDER BY a.created_at DESC
            LIMIT ?
            """
        )
        params = (user_id, limit)

    with get_connection(db_path) as conn:
        rows = conn.execute(query, params).fetchall()
    return [dict(r) for r in rows]
