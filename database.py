import sqlite3
import config


def get_connection() -> sqlite3.Connection:
    return sqlite3.connect(config.DB_PATH)


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS content (
            video_id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            published_at TEXT NOT NULL,
            duration_seconds INTEGER,
            content_type TEXT
        );

        CREATE TABLE IF NOT EXISTS engagement (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id TEXT NOT NULL,
            snapshot_date TEXT NOT NULL,
            views INTEGER,
            likes INTEGER,
            comments INTEGER,
            engagement_rate REAL,
            UNIQUE(video_id, snapshot_date),
            FOREIGN KEY (video_id) REFERENCES content(video_id)
        );
    """)
    conn.commit()


def upsert_content(conn, video_id, title, published_at, duration_seconds, content_type) -> None:
    conn.execute("""
        INSERT INTO content (video_id, title, published_at, duration_seconds, content_type)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(video_id) DO UPDATE SET title = excluded.title
    """, (video_id, title, published_at, duration_seconds, content_type))
    conn.commit()


def insert_engagement_snapshot(conn, video_id, snapshot_date, views, likes, comments, engagement_rate) -> None:
    conn.execute("""
        INSERT INTO engagement (video_id, snapshot_date, views, likes, comments, engagement_rate)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(video_id, snapshot_date) DO UPDATE SET
            views = excluded.views,
            likes = excluded.likes,
            comments = excluded.comments,
            engagement_rate = excluded.engagement_rate
    """, (video_id, snapshot_date, views, likes, comments, engagement_rate))
    conn.commit() 