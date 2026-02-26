#!/usr/bin/env python3
"""Fetch AI-related hotspots from Reddit and persist to data/hotspots.json.

Designed for GitHub Actions scheduled runs ("compromise deployment" mode).
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

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


def _build_url(subreddit: str, limit: int) -> str:
    params = urllib.parse.urlencode({"limit": str(limit), "raw_json": "1"})
    return f"https://www.reddit.com/r/{subreddit}/hot.json?{params}"


def _request_json(url: str) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": _user_agent()})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def _to_iso_utc(ts: float) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()


def _clean_summary(text: str, fallback: str) -> str:
    body = (text or "").strip().replace("\n", " ")
    if body:
        return body[:180]
    return fallback[:180]


def fetch(subreddits: Iterable[str], limit: int) -> list[Hotspot]:
    now = datetime.now(timezone.utc).isoformat()
    seen_ids: set[str] = set()
    results: list[Hotspot] = []

    for subreddit in subreddits:
        url = _build_url(subreddit, limit)
        payload = _request_json(url)
        posts = payload.get("data", {}).get("children", [])

        for post in posts:
            data = post.get("data", {})
            post_id = data.get("id")
            if not post_id or post_id in seen_ids:
                continue

            seen_ids.add(post_id)
            permalink = data.get("permalink") or ""
            source_url = f"https://www.reddit.com{permalink}" if permalink.startswith("/") else data.get("url", "")
            title = (data.get("title") or "").strip()

            results.append(
                Hotspot(
                    source="reddit",
                    source_post_id=post_id,
                    subreddit=subreddit,
                    title=title,
                    summary=_clean_summary(data.get("selftext", ""), title),
                    source_url=source_url,
                    author=data.get("author", ""),
                    score=int(data.get("score", 0)),
                    num_comments=int(data.get("num_comments", 0)),
                    published_at=_to_iso_utc(float(data.get("created_utc", 0))),
                    fetched_at=now,
                )
            )

    results.sort(key=lambda x: (x.score, x.num_comments), reverse=True)
    return results


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
    except (urllib.error.URLError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
        print(f"[error] failed to update hotspots: {exc}", file=sys.stderr)
        return 1

    print(f"updated {OUTPUT_PATH} with {len(items)} hotspots from {len(subreddits)} subreddits")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
