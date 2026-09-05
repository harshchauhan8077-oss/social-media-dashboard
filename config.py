"""
Central configuration. All values are loaded from environment variables
(see .env.example) so no secrets are ever hard-coded or committed to git.
"""
import os
from dotenv import load_dotenv

load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
YOUTUBE_CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID")

DB_PATH = os.getenv("DB_PATH", "data/social_media.db")
EXPORT_DIR = os.getenv("EXPORT_DIR", "data/exports")

os.makedirs(os.path.dirname(DB_PATH) or ".", exist_ok=True)

if not YOUTUBE_API_KEY or not YOUTUBE_CHANNEL_ID:
    raise EnvironmentError(
        "YOUTUBE_API_KEY and YOUTUBE_CHANNEL_ID must be set. "
        "Copy .env.example to .env and fill in your values."
    ) 