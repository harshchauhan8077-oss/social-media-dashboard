import os

import pandas as pd

import config
import database

MIN_POSTS_PER_SLOT = 3


def load_data() -> pd.DataFrame:
    conn = database.get_connection()
    df = pd.read_sql_query("""
        SELECT c.video_id, c.title, c.published_at, c.content_type,
               e.views, e.likes, e.comments, e.engagement_rate
        FROM content c
        JOIN engagement e ON c.video_id = e.video_id
    """, conn)
    conn.close()
    return df


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    df["published_at"] = pd.to_datetime(df["published_at"])
    df["day_of_week"] = df["published_at"].dt.day_name()
    df["hour"] = df["published_at"].dt.hour
    return df


def top_content(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    return df.sort_values("engagement_rate", ascending=False).head(n)


def content_type_performance(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("content_type").agg(
        avg_engagement_rate=("engagement_rate", "mean"),
        avg_views=("views", "mean"),
        post_count=("video_id", "count"),
    ).reset_index()


def best_posting_slots(df: pd.DataFrame, min_sample: int = MIN_POSTS_PER_SLOT) -> pd.DataFrame:
    grouped = df.groupby(["day_of_week", "hour"]).agg(
        avg_engagement_rate=("engagement_rate", "mean"),
        post_count=("video_id", "count"),
    ).reset_index()
    grouped = grouped[grouped["post_count"] >= min_sample]
    return grouped.sort_values("avg_engagement_rate", ascending=False)


def run() -> None:
    df = load_data()
    if df.empty:
        print("No data found. Run 'python main.py sync' first.")
        return
    df = add_time_features(df)

    print("\n=== TOP 10 CONTENT BY ENGAGEMENT RATE ===")
    print(top_content(df)[["title", "views", "likes", "comments", "engagement_rate"]].to_string(index=False))

    print("\n=== CONTENT TYPE PERFORMANCE ===")
    print(content_type_performance(df).to_string(index=False))

    slots = best_posting_slots(df)
    print(f"\n=== BEST POSTING SLOTS (min {MIN_POSTS_PER_SLOT} posts per slot) ===")
    if slots.empty:
        print("Not enough historical data yet — need more posts per day/hour combination.")
    else:
        print(slots.head(5).to_string(index=False))

    os.makedirs(config.EXPORT_DIR, exist_ok=True)
    slots.to_csv(os.path.join(config.EXPORT_DIR, "posting_time_recommendations.csv"), index=False)


if __name__ == "__main__":
    run() 