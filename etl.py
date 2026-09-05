import os
from datetime import date

import pandas as pd

import config
import database
from youtube_client import YouTubeClient


def calc_engagement_rate(likes: int, comments: int, views: int) -> float:
    if not views:
        return 0.0
    return round((likes + comments) / views * 100, 4)


def classify_content_type(duration_seconds: int) -> str:
    return "SHORT" if duration_seconds and duration_seconds <= 60 else "VIDEO"


def export_csv_for_powerbi(conn) -> None:
    os.makedirs(config.EXPORT_DIR, exist_ok=True)
    df = pd.read_sql_query("""
        SELECT c.video_id, c.title, c.published_at, c.content_type,
               e.snapshot_date, e.views, e.likes, e.comments, e.engagement_rate
        FROM content c
        JOIN engagement e ON c.video_id = e.video_id
        ORDER BY e.snapshot_date DESC
    """, conn)
    df.to_csv(os.path.join(config.EXPORT_DIR, "engagement_export.csv"), index=False)


def run() -> None:
    conn = database.get_connection()
    database.init_db(conn)

    client = YouTubeClient(config.YOUTUBE_API_KEY)
    videos = client.fetch_channel_videos(config.YOUTUBE_CHANNEL_ID)
    today = date.today().isoformat()

    for v in videos:
        content_type = classify_content_type(v["duration_seconds"])
        database.upsert_content(
            conn, v["video_id"], v["title"], v["published_at"],
            v["duration_seconds"], content_type,
        )
        rate = calc_engagement_rate(v["like_count"], v["comment_count"], v["view_count"])
        database.insert_engagement_snapshot(
            conn, v["video_id"], today,
            v["view_count"], v["like_count"], v["comment_count"], rate,
        )

    export_csv_for_powerbi(conn)
    conn.close()
    print(f"Synced {len(videos)} videos. CSV exported to {config.EXPORT_DIR}/engagement_export.csv")


if __name__ == "__main__":
    run() 