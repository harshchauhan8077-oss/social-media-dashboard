"""
Thin wrapper around the official YouTube Data API v3.
Only fetches what the dashboard needs: video metadata + public stats.
"""
import re
from googleapiclient.discovery import build


class YouTubeClient:
    def __init__(self, api_key: str):
        self.youtube = build("youtube", "v3", developerKey=api_key)

    def fetch_channel_videos(self, channel_id: str) -> list[dict]:
        """Returns a list of dicts, one per public video on the channel."""
        playlist_id = self._get_uploads_playlist_id(channel_id)
        video_ids = self._get_video_ids(playlist_id)
        return self._get_video_details(video_ids)

    def _get_uploads_playlist_id(self, channel_id: str) -> str:
        resp = self.youtube.channels().list(
            part="contentDetails", id=channel_id
        ).execute()
        if not resp["items"]:
            raise ValueError(f"No channel found for id: {channel_id}")
        return resp["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

    def _get_video_ids(self, playlist_id: str) -> list[str]:
        video_ids, next_page_token = [], None
        while True:
            resp = self.youtube.playlistItems().list(
                part="contentDetails",
                playlistId=playlist_id,
                maxResults=50,
                pageToken=next_page_token,
            ).execute()
            video_ids.extend(item["contentDetails"]["videoId"] for item in resp["items"])
            next_page_token = resp.get("nextPageToken")
            if not next_page_token:
                return video_ids

    def _get_video_details(self, video_ids: list[str]) -> list[dict]:
        videos = []
        for i in range(0, len(video_ids), 50):  # API allows max 50 ids per call
            batch = video_ids[i:i + 50]
            resp = self.youtube.videos().list(
                part="snippet,statistics,contentDetails", id=",".join(batch)
            ).execute()
            for item in resp["items"]:
                stats = item.get("statistics", {})
                videos.append({
                    "video_id": item["id"],
                    "title": item["snippet"]["title"],
                    "published_at": item["snippet"]["publishedAt"],
                    "duration_seconds": self._parse_duration(item["contentDetails"]["duration"]),
                    "view_count": int(stats.get("viewCount", 0)),
                    "like_count": int(stats.get("likeCount", 0)),
                    "comment_count": int(stats.get("commentCount", 0)),
                })
        return videos

    @staticmethod
    def _parse_duration(iso_duration: str) -> int:
        """Converts ISO 8601 duration (e.g. 'PT4M13S') to total seconds."""
        match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso_duration)
        if not match:
            return 0
        hours, minutes, seconds = (int(x) if x else 0 for x in match.groups())
        return hours * 3600 + minutes * 60 + seconds 