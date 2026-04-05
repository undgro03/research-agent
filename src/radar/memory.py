"""SQLite memory store — deduplication, trend tracking, alert logging."""
from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

DB_PATH = Path(__file__).parent.parent.parent / "data" / "radar.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS items (
    id          TEXT PRIMARY KEY,
    source      TEXT NOT NULL,
    url         TEXT NOT NULL,
    title       TEXT,
    authors     TEXT,
    abstract    TEXT,
    published   DATETIME,
    first_seen  DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_seen   DATETIME DEFAULT CURRENT_TIMESTAMP,
    seen_count  INTEGER DEFAULT 1,
    theme_slugs TEXT DEFAULT '[]',
    score       REAL,
    alerted     INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS trend_snapshots (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    theme_slug  TEXT NOT NULL,
    snapshot_dt DATETIME DEFAULT CURRENT_TIMESTAMP,
    cluster     TEXT NOT NULL,
    item_count  INTEGER,
    trend_score REAL,
    top_items   TEXT DEFAULT '[]'
);

CREATE TABLE IF NOT EXISTS reports (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    report_type TEXT NOT NULL,
    theme_slug  TEXT,
    report_date DATE,
    file_path   TEXT,
    items_count INTEGER DEFAULT 0,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS alerts (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id      TEXT REFERENCES items(id),
    alert_type   TEXT,
    triggered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    notified     INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS articles (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    theme_slug  TEXT NOT NULL,
    title_ja    TEXT,
    title_en    TEXT,
    slug        TEXT,
    article_date DATE,
    file_path_md  TEXT,
    file_path_html TEXT,
    score       REAL,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""


def get_connection(db_path: Path = DB_PATH) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Path = DB_PATH) -> None:
    with get_connection(db_path) as conn:
        conn.executescript(SCHEMA)
    print(f"Database initialized at {db_path}")


def make_item_id(source: str, url: str) -> str:
    return hashlib.sha256(f"{source}::{url}".encode()).hexdigest()[:16]


def upsert_item(
    source: str,
    url: str,
    title: str = "",
    authors: list[str] | None = None,
    abstract: str = "",
    published: Optional[datetime] = None,
    theme_slugs: list[str] | None = None,
    score: Optional[float] = None,
    db_path: Path = DB_PATH,
) -> tuple[str, bool]:
    """Insert or update an item. Returns (item_id, is_new)."""
    item_id = make_item_id(source, url)
    now = datetime.utcnow().isoformat()

    with get_connection(db_path) as conn:
        existing = conn.execute(
            "SELECT id, seen_count, theme_slugs FROM items WHERE id = ?", (item_id,)
        ).fetchone()

        if existing:
            existing_themes = json.loads(existing["theme_slugs"] or "[]")
            merged_themes = list(set(existing_themes + (theme_slugs or [])))
            conn.execute(
                """UPDATE items
                   SET last_seen = ?, seen_count = seen_count + 1,
                       theme_slugs = ?, score = COALESCE(?, score)
                   WHERE id = ?""",
                (now, json.dumps(merged_themes), score, item_id),
            )
            return item_id, False
        else:
            conn.execute(
                """INSERT INTO items
                   (id, source, url, title, authors, abstract, published,
                    first_seen, last_seen, theme_slugs, score)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    item_id, source, url, title,
                    json.dumps(authors or []),
                    abstract,
                    published.isoformat() if published else None,
                    now, now,
                    json.dumps(theme_slugs or []),
                    score,
                ),
            )
            return item_id, True


def is_seen(source: str, url: str, db_path: Path = DB_PATH) -> bool:
    item_id = make_item_id(source, url)
    with get_connection(db_path) as conn:
        row = conn.execute("SELECT id FROM items WHERE id = ?", (item_id,)).fetchone()
    return row is not None


def log_report(
    report_type: str,
    file_path: str,
    theme_slug: str = "",
    items_count: int = 0,
    db_path: Path = DB_PATH,
) -> None:
    today = datetime.utcnow().date().isoformat()
    with get_connection(db_path) as conn:
        conn.execute(
            """INSERT INTO reports (report_type, theme_slug, report_date, file_path, items_count)
               VALUES (?, ?, ?, ?, ?)""",
            (report_type, theme_slug, today, file_path, items_count),
        )


def log_alert(item_id: str, alert_type: str, db_path: Path = DB_PATH) -> None:
    with get_connection(db_path) as conn:
        conn.execute(
            "INSERT INTO alerts (item_id, alert_type) VALUES (?, ?)",
            (item_id, alert_type),
        )
        conn.execute("UPDATE items SET alerted = 1 WHERE id = ?", (item_id,))


def prune_old_items(days: int = 90, db_path: Path = DB_PATH) -> int:
    cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
    with get_connection(db_path) as conn:
        cur = conn.execute("DELETE FROM items WHERE first_seen < ?", (cutoff,))
    return cur.rowcount
