"""
SQLite data layer — stdlib only, zero configuration, works on any machine.

Ritu stores daily symptom logs. Nothing else. No name, no email, no phone,
no location — a woman should not have to surrender her identity to understand
her own cycle.
"""
from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from typing import Iterator

DB_PATH = os.getenv("DB_PATH", "app.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS logs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    profile         TEXT    NOT NULL DEFAULT 'me',
    log_date        TEXT    NOT NULL,
    cycle_day       INTEGER,
    is_period_start INTEGER NOT NULL DEFAULT 0,
    flow            TEXT    NOT NULL DEFAULT 'none',
    pain            INTEGER NOT NULL DEFAULT 0,
    symptoms        TEXT    NOT NULL DEFAULT '[]',
    notes           TEXT    NOT NULL DEFAULT ''
);
CREATE INDEX IF NOT EXISTS idx_logs_profile_date ON logs(profile, log_date);
CREATE UNIQUE INDEX IF NOT EXISTS idx_logs_profile_day ON logs(profile, log_date);
"""


@contextmanager
def get_conn() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    """Create schema. Safe to call on every startup."""
    with get_conn() as conn:
        conn.executescript(SCHEMA)


def reset_profile(profile: str) -> None:
    with get_conn() as conn:
        conn.execute("DELETE FROM logs WHERE profile = ?", (profile,))


def insert_logs(rows: list[tuple]) -> int:
    with get_conn() as conn:
        conn.executemany(
            """INSERT OR REPLACE INTO logs
               (profile, log_date, cycle_day, is_period_start, flow, pain, symptoms, notes)
               VALUES (?,?,?,?,?,?,?,?)""",
            rows,
        )
        return conn.execute("SELECT COUNT(*) FROM logs").fetchone()[0]


def latest_period_start(profile: str, on_or_before: str) -> str | None:
    """Most recent period start on or before a date — used to compute cycle day."""
    with get_conn() as conn:
        row = conn.execute(
            """SELECT log_date FROM logs
               WHERE profile = ? AND is_period_start = 1 AND log_date <= ?
               ORDER BY log_date DESC LIMIT 1""",
            (profile, on_or_before),
        ).fetchone()
    return row["log_date"] if row else None
