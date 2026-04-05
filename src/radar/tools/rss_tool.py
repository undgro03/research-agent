"""RSS/Atom feed reader for lab blogs and news sources."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

import feedparser
import httpx
import yaml

FEEDS_PATH = Path(__file__).parent.parent.parent.parent / "data" / "feeds.yaml"


@dataclass
class FeedItem:
    title: str
    url: str
    summary: str
    published: datetime
    source_name: str
    source: str = "rss"
    tags: list[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


async def fetch_feed(url: str, source_name: str, tags: list[str] = None) -> list[FeedItem]:
    """Fetch and parse a single RSS/Atom feed."""
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            resp = await client.get(url, headers={"User-Agent": "EmbodiedAIRadar/0.1"})
            resp.raise_for_status()
            content = resp.text
    except Exception as e:
        print(f"[rss] Failed to fetch {url}: {e}")
        return []

    feed = feedparser.parse(content)
    items = []

    for entry in feed.entries[:20]:
        try:
            published = None
            for attr in ("published_parsed", "updated_parsed", "created_parsed"):
                val = getattr(entry, attr, None)
                if val:
                    published = datetime(*val[:6])
                    break
            if published is None:
                published = datetime.utcnow()

            summary = getattr(entry, "summary", "") or getattr(entry, "description", "") or ""
            summary = summary[:500]

            items.append(FeedItem(
                title=getattr(entry, "title", ""),
                url=getattr(entry, "link", ""),
                summary=summary,
                published=published,
                source_name=source_name,
                tags=tags or [],
            ))
        except Exception:
            continue

    return items


async def fetch_all_feeds(feeds_path: Path = FEEDS_PATH) -> list[FeedItem]:
    """Fetch all configured RSS feeds in parallel."""
    feeds_config = yaml.safe_load(feeds_path.read_text())
    rss_feeds = feeds_config.get("rss_feeds", [])

    tasks = [
        fetch_feed(f["url"], f["name"], f.get("tags", []))
        for f in rss_feeds
        if f.get("url")
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)
    items = []
    for r in results:
        if isinstance(r, list):
            items.extend(r)

    return items
