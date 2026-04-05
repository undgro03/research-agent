"""X (Twitter) API v2 client — read-only monitoring via Bearer Token."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Optional

import httpx
from dotenv import load_dotenv

load_dotenv()

TWITTER_API_BASE = "https://api.twitter.com/2"


@dataclass
class Tweet:
    id: str
    url: str
    text: str
    author_id: str
    author_name: str
    author_handle: str
    created_at: datetime
    like_count: int = 0
    retweet_count: int = 0
    reply_count: int = 0
    source: str = "twitter"

    @property
    def engagement(self) -> int:
        return self.like_count + self.retweet_count


class TwitterClient:
    def __init__(self, bearer_token: Optional[str] = None):
        self.bearer_token = bearer_token or os.environ.get("TWITTER_BEARER_TOKEN", "")
        self._headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "User-Agent": "EmbodiedAIRadar/0.1",
        }

    async def search_recent(
        self,
        keywords: list[str],
        lookback_hours: int = 24,
        max_results: int = 100,
    ) -> list[Tweet]:
        """Search recent tweets by keywords (last 7 days max on Basic tier)."""
        if not self.bearer_token:
            print("[twitter] No bearer token — skipping Twitter search")
            return []

        since = datetime.now(timezone.utc) - timedelta(hours=lookback_hours)
        since_str = since.strftime("%Y-%m-%dT%H:%M:%SZ")

        # Build query: OR of keywords, exclude retweets
        kw_parts = [f'"{k}"' for k in keywords[:5]]  # API limit
        query = "(" + " OR ".join(kw_parts) + ") -is:retweet lang:en"

        params = {
            "query": query,
            "max_results": min(max_results, 100),
            "start_time": since_str,
            "tweet.fields": "created_at,public_metrics,author_id",
            "user.fields": "name,username",
            "expansions": "author_id",
        }

        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.get(
                f"{TWITTER_API_BASE}/tweets/search/recent",
                headers=self._headers,
                params=params,
            )
            if resp.status_code == 401:
                print("[twitter] 401 Unauthorized — check Bearer Token")
                return []
            if resp.status_code == 429:
                print("[twitter] 429 Rate limited")
                return []
            resp.raise_for_status()

        return self._parse_response(resp.json())

    async def get_user_timeline(
        self,
        username: str,
        lookback_hours: int = 24,
        max_results: int = 20,
    ) -> list[Tweet]:
        """Fetch recent tweets from a specific user."""
        if not self.bearer_token:
            return []

        # First get user ID
        async with httpx.AsyncClient(timeout=20) as client:
            user_resp = await client.get(
                f"{TWITTER_API_BASE}/users/by/username/{username}",
                headers=self._headers,
                params={"user.fields": "name,username"},
            )
            if user_resp.status_code != 200:
                return []
            user_data = user_resp.json().get("data", {})
            user_id = user_data.get("id")
            if not user_id:
                return []

        since = datetime.now(timezone.utc) - timedelta(hours=lookback_hours)
        params = {
            "max_results": min(max_results, 100),
            "start_time": since.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "tweet.fields": "created_at,public_metrics",
            "exclude": "retweets",
        }

        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.get(
                f"{TWITTER_API_BASE}/users/{user_id}/tweets",
                headers=self._headers,
                params=params,
            )
            if resp.status_code != 200:
                return []

        tweets = self._parse_response(resp.json())
        # Fill in author info from what we already have
        for t in tweets:
            t.author_name = user_data.get("name", username)
            t.author_handle = username
        return tweets

    def _parse_response(self, data: dict) -> list[Tweet]:
        tweets_data = data.get("data", [])
        users_map = {
            u["id"]: u
            for u in data.get("includes", {}).get("users", [])
        }

        tweets = []
        for t in tweets_data:
            metrics = t.get("public_metrics", {})
            author = users_map.get(t.get("author_id", ""), {})
            tweet_id = t["id"]

            tweets.append(Tweet(
                id=tweet_id,
                url=f"https://twitter.com/i/web/status/{tweet_id}",
                text=t.get("text", ""),
                author_id=t.get("author_id", ""),
                author_name=author.get("name", ""),
                author_handle=author.get("username", ""),
                created_at=datetime.fromisoformat(
                    t.get("created_at", "2024-01-01T00:00:00Z").replace("Z", "+00:00")
                ).replace(tzinfo=None),
                like_count=metrics.get("like_count", 0),
                retweet_count=metrics.get("retweet_count", 0),
                reply_count=metrics.get("reply_count", 0),
            ))

        return tweets
