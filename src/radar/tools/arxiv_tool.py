"""arXiv API wrapper — search and fetch paper metadata."""
from __future__ import annotations

import asyncio
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional
from urllib.parse import quote

import httpx

ARXIV_API = "https://export.arxiv.org/api/query"
ARXIV_NS = {"atom": "http://www.w3.org/2005/Atom"}


@dataclass
class ArxivPaper:
    id: str
    url: str
    title: str
    authors: list[str]
    abstract: str
    published: datetime
    categories: list[str]
    source: str = "arxiv"


async def search(
    keywords: list[str],
    categories: list[str],
    max_results: int = 50,
    lookback_days: int = 1,
) -> list[ArxivPaper]:
    """Search arXiv for papers matching keywords within lookback_days."""
    since = datetime.utcnow() - timedelta(days=lookback_days)
    since_str = since.strftime("%Y%m%d")

    # Build query
    cat_query = " OR ".join(f"cat:{c}" for c in categories)
    kw_query = " OR ".join(f'all:"{k}"' for k in keywords[:10])  # limit to 10 keywords
    date_query = f"submittedDate:[{since_str}0000 TO *]"
    query = f"({cat_query}) AND ({kw_query}) AND {date_query}"

    params = {
        "search_query": query,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(ARXIV_API, params=params)
        resp.raise_for_status()

    return _parse_feed(resp.text)


def _parse_feed(xml_text: str) -> list[ArxivPaper]:
    root = ET.fromstring(xml_text)
    papers = []

    for entry in root.findall("atom:entry", ARXIV_NS):
        try:
            arxiv_id = entry.find("atom:id", ARXIV_NS).text.strip()
            title = entry.find("atom:title", ARXIV_NS).text.strip().replace("\n", " ")
            abstract = entry.find("atom:summary", ARXIV_NS).text.strip().replace("\n", " ")
            published_str = entry.find("atom:published", ARXIV_NS).text.strip()
            published = datetime.fromisoformat(published_str.replace("Z", "+00:00"))

            authors = [
                a.find("atom:name", ARXIV_NS).text.strip()
                for a in entry.findall("atom:author", ARXIV_NS)
            ]

            categories = [
                t.get("term")
                for t in entry.findall("atom:category", ARXIV_NS)
            ]

            # Normalize URL to abs link
            url = arxiv_id if arxiv_id.startswith("http") else f"https://arxiv.org/abs/{arxiv_id}"

            papers.append(ArxivPaper(
                id=arxiv_id,
                url=url,
                title=title,
                authors=authors,
                abstract=abstract[:500],
                published=published.replace(tzinfo=None),
                categories=[c for c in categories if c],
            ))
        except Exception:
            continue

    return papers


async def fetch_recent_by_category(category: str, max_results: int = 30) -> list[ArxivPaper]:
    """Fetch latest papers from a specific arXiv category via RSS."""
    rss_url = f"https://rss.arxiv.org/rss/{category}"
    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.get(rss_url)
        resp.raise_for_status()

    # RSS parsing (simpler than Atom)
    papers = []
    root = ET.fromstring(resp.text)
    channel = root.find("channel")
    if channel is None:
        return papers

    for i, item in enumerate(channel.findall("item")):
        if i >= max_results:
            break
        try:
            title_el = item.find("title")
            link_el = item.find("link")
            desc_el = item.find("description")
            title = title_el.text.strip() if title_el is not None else ""
            url = link_el.text.strip() if link_el is not None else ""
            abstract = desc_el.text.strip()[:500] if desc_el is not None else ""

            papers.append(ArxivPaper(
                id=url,
                url=url,
                title=title,
                authors=[],
                abstract=abstract,
                published=datetime.utcnow(),
                categories=[category],
            ))
        except Exception:
            continue

    return papers


if __name__ == "__main__":
    async def _test():
        papers = await search(
            keywords=["embodied AI", "VLA model"],
            categories=["cs.RO", "cs.LG"],
            max_results=5,
        )
        for p in papers:
            print(f"[{p.published.date()}] {p.title[:80]} — {p.url}")

    asyncio.run(_test())
