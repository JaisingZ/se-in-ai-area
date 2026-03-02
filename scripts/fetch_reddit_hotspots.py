#!/usr/bin/env python3
"""Fetch AI-related hotspots from Reddit and persist to data/hotspots.json.

Designed for GitHub Actions scheduled runs ("compromise deployment" mode).
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ingestion.reddit_hot import RedditClient, sort_hot_posts

DEFAULT_SUBREDDITS = ["MachineLearning", "artificial", "LocalLLaMA", "AI_Agents"]
DEFAULT_LIMIT = 20
OUTPUT_PATH = Path("data/hotspots.json")


@dataclass
class Hotspot:
    source: str
    source_post_id: str
    subreddit: str
    title: str
    summary: str
    source_url: str
    author: str
    score: int
    num_comments: int
    published_at: str
    fetched_at: str


def _env_list(name: str, default: list[str]) -> list[str]:
    raw = os.getenv(name, "")
    if not raw.strip():
        return default
    return [item.strip() for item in raw.split(",") if item.strip()]


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default

    try:
        value = int(raw)
    except ValueError:
        return default

    return value if value > 0 else default


def _env_str(name: str, default: str) -> str:
    raw = os.getenv(name, "")
    return raw.strip() or default


def _user_agent() -> str:
    return _env_str("REDDIT_USER_AGENT", "se-in-ai-area/0.1 (by github-actions)")


def _to_iso_utc(ts: float) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()


def _clean_summary(text: str, fallback: str) -> str:
    body = (text or "").strip().replace("\n", " ")
    if body:
        return body[:180]
    return fallback[:180]


def fetch(subreddits: Iterable[str], limit: int) -> list[Hotspot]:
    now = datetime.now(timezone.utc).isoformat()
    client = RedditClient(user_agent=_user_agent(), timeout_seconds=30)
    posts = sort_hot_posts(client.fetch_hot_posts_for_subreddits(subreddits, limit_per_subreddit=limit, sleep_seconds=0.2))

    return [
        Hotspot(
            source="reddit",
            source_post_id=post.post_id,
            subreddit=post.subreddit,
            title=post.title,
            summary=_clean_summary("", post.title),
            source_url=post.url,
            author=post.author,
            score=post.score,
            num_comments=post.num_comments,
            published_at=_to_iso_utc(post.created_utc),
            fetched_at=now,
        )
        for post in posts
    ]


def save(items: list[Hotspot], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "count": len(items),
        "items": [asdict(item) for item in items],
    }
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    subreddits = _env_list("REDDIT_SUBREDDITS", DEFAULT_SUBREDDITS)
    limit = _env_int("REDDIT_LIMIT", DEFAULT_LIMIT)

    try:
        items = fetch(subreddits, limit)
        save(items, OUTPUT_PATH)
    except urllib.error.HTTPError as exc:
        if exc.code in (403, 429):
            print(
                f"[warn] reddit returned HTTP {exc.code}. Skipping update to keep workflow green.",
                file=sys.stderr,
            )
            return 0
        print(f"[error] failed to update hotspots: {exc}", file=sys.stderr)
        return 1
    except (urllib.error.URLError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
        print(f"[error] failed to update hotspots: {exc}", file=sys.stderr)
        return 1

    print(f"updated {OUTPUT_PATH} with {len(items)} hotspots from {len(subreddits)} subreddits")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
