import sqlite3

from app.config import DEFAULT_BOUNDARY_MODE, DEFAULT_PEAK_FACTOR
from app.engines.tier_progressive import BOUNDARY_MODES


def get_map(conn: sqlite3.Connection) -> dict[str, str]:
    return {r["key"]: r["value"] for r in conn.execute("SELECT * FROM settings").fetchall()}


def peak_factor(conn: sqlite3.Connection) -> float:
    row = conn.execute("SELECT value FROM settings WHERE key='peak_factor'").fetchone()
    if not row:
        return DEFAULT_PEAK_FACTOR
    return float(row["value"])


def boundary_mode(conn: sqlite3.Connection) -> str:
    row = conn.execute("SELECT value FROM settings WHERE key='boundary_mode'").fetchone()
    if not row or row["value"] not in BOUNDARY_MODES:
        return DEFAULT_BOUNDARY_MODE
    return row["value"]


def set_value(conn: sqlite3.Connection, key: str, value: str) -> None:
    conn.execute(
        "INSERT INTO settings(key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (key, value),
    )
    conn.commit()
