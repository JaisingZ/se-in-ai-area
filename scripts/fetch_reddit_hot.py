#!/usr/bin/env python3
"""CLI script to fetch hot posts from Reddit and save JSON output."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ingestion.reddit_hot import RedditClient, sort_hot_posts


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Fetch hot Reddit posts for AI/programming subreddits")
    parser.add_argument(
        "--subreddits",
        default="MachineLearning,LocalLLaMA,programming,learnprogramming,OpenAI",
        help="Comma-separated subreddit names",
    )
    parser.add_argument("--limit", type=int, default=20, help="Hot post limit per subreddit")
    parser.add_argument("--output", default="data/reddit_hot.json", help="Output JSON file path")
    parser.add_argument("--user-agent", default=None, help="Custom User-Agent header")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    subreddits = [item.strip() for item in args.subreddits.split(",") if item.strip()]

    client = RedditClient(user_agent=args.user_agent) if args.user_agent else RedditClient()
    posts = client.fetch_hot_posts_for_subreddits(
        subreddits=subreddits,
        limit_per_subreddit=args.limit,
        sleep_seconds=0.2,
    )
    sorted_posts = sort_hot_posts(posts)

    payload = {
        "subreddits": subreddits,
        "count": len(sorted_posts),
        "items": [post.to_dict() for post in sorted_posts],
    }

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Saved {len(sorted_posts)} posts to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
