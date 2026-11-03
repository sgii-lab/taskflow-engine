
import sqlite3

from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path


class Database:

    def __init__(self, db_path="data/taskflow.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    @contextmanager
    def connect(self):
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")

        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def initialize(self):
        with self.connect() as connection:

            connection.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    handler TEXT NOT NULL,
                    args_json TEXT NOT NULL DEFAULT '{}',
                    interval_seconds INTEGER,
                    next_run_at TEXT,
                    enabled INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL
                )
            """)

            connection.execute("""
                CREATE TABLE IF NOT EXISTS task_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    finished_at TEXT,
                    duration REAL,
                    output TEXT,
                    error TEXT,
                    FOREIGN KEY(task_id)
                        REFERENCES tasks(id)
                        ON DELETE CASCADE
                )
            """)

    def add_task(
        self,
        name,
        handler,
        args_json="{}",
        interval_seconds=None,
        next_run_at=None
    ):
        with self.connect() as connection:
            cursor = connection.execute("""
                INSERT INTO tasks (
                    name,
                    handler,
                    args_json,
                    interval_seconds,
                    next_run_at,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                name,
                handler,
                args_json,
                interval_seconds,
                next_run_at,
                datetime.now(timezone.utc).isoformat()
            ))

            return cursor.lastrowid

    def get_task(self, task_id):
        with self.connect() as connection:
            return connection.execute(
                "SELECT * FROM tasks WHERE id = ?",
                (task_id,)
            ).fetchone()

    def list_tasks(self):
        with self.connect() as connection:
            return connection.execute(
                "SELECT * FROM tasks ORDER BY id"
            ).fetchall()

    def set_enabled(self, task_id, enabled):
        with self.connect() as connection:
            cursor = connection.execute("""
                UPDATE tasks
                SET enabled = ?
                WHERE id = ?
            """, (int(enabled), task_id))

            return cursor.rowcount > 0

    def delete_task(self, task_id):
        with self.connect() as connection:
            cursor = connection.execute(
                "DELETE FROM tasks WHERE id = ?",
                (task_id,)
            )

            return cursor.rowcount > 0

    def record_run(
        self,
        task_id,
        status,
        started_at,
        finished_at,
        duration,
        output=None,
        error=None
    ):
        with self.connect() as connection:
            cursor = connection.execute("""
                INSERT INTO task_runs (
                    task_id,
                    status,
                    started_at,
                    finished_at,
                    duration,
                    output,
                    error
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                task_id,
                status,
                started_at,
                finished_at,
                duration,
                output,
                error
            ))

            return cursor.lastrowid

    def get_history(self, task_id=None, limit=20):
        with self.connect() as connection:

            if task_id is not None:
                return connection.execute("""
                    SELECT * FROM task_runs
                    WHERE task_id = ?
                    ORDER BY id DESC
                    LIMIT ?
                """, (task_id, limit)).fetchall()

            return connection.execute("""
                SELECT * FROM task_runs
                ORDER BY id DESC
                LIMIT ?
            """, (limit,)).fetchall()

    def get_due_tasks(self, current_time):
        with self.connect() as connection:
            return connection.execute("""
                SELECT *
                FROM tasks
                WHERE enabled = 1
                  AND interval_seconds IS NOT NULL
                  AND next_run_at IS NOT NULL
                  AND next_run_at <= ?
                ORDER BY next_run_at ASC
            """, (current_time,)).fetchall()

    def update_next_run(self, task_id, next_run_at):
        with self.connect() as connection:
            cursor = connection.execute("""
                UPDATE tasks
                SET next_run_at = ?
                WHERE id = ?
            """, (next_run_at, task_id))

            return cursor.rowcount > 0
