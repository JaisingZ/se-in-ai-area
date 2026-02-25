"""Utilities for fetching hot Reddit posts for AI/programming topics via Reddit RSS feeds."""

from __future__ import annotations

from dataclasses import dataclass, asdict
from email.utils import parsedate_to_datetime
import re
import time
from typing import Iterable, List
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from xml.etree import ElementTree


REDDIT_BASE_URL = "https://www.reddit.com"
ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}
DEFAULT_USER_AGENT = "se-in-ai-area-bot/0.2 (+https://www.reddit.com/)"

_SCORE_RE = re.compile(r"^(?P<score>\d+) points?")
_COMMENTS_RE = re.compile(r"(?P<comments>\d+) comments?")


@dataclass
class RedditPost:
    post_id: str
    subreddit: str
    title: str
    author: str
    score: int
    num_comments: int
    created_utc: float
    permalink: str
    url: str
    is_self: bool
    over_18: bool

    def to_dict(self) -> dict:
        return asdict(self)


class RedditClient:
    def __init__(self, user_agent: str = DEFAULT_USER_AGENT, timeout_seconds: int = 15):
        self.user_agent = user_agent
        self.timeout_seconds = timeout_seconds

    def fetch_hot_posts(self, subreddit: str, limit: int = 25) -> List[RedditPost]:
        if limit <= 0:
            raise ValueError("limit must be > 0")

        query = urlencode({"limit": limit})
        url = f"{REDDIT_BASE_URL}/r/{subreddit}/hot/.rss?{query}"
        req = Request(url, headers={"User-Agent": self.user_agent})

        with urlopen(req, timeout=self.timeout_seconds) as response:
            xml_payload = response.read().decode("utf-8")

        root = ElementTree.fromstring(xml_payload)
        posts: List[RedditPost] = []

        for entry in root.findall("atom:entry", ATOM_NS):
            post_id = self._get_text(entry, "atom:id").split(":")[-1]
            title = self._get_text(entry, "atom:title")
            author = self._get_text(entry, "atom:author/atom:name")
            published = self._get_text(entry, "atom:updated") or self._get_text(entry, "atom:published")
            created_utc = (
                parsedate_to_datetime(published).timestamp() if published and "," in published else 0.0
            )

            link = entry.find("atom:link", ATOM_NS)
            permalink = link.attrib.get("href", "") if link is not None else ""

            summary = self._get_text(entry, "atom:content")
            score = self._extract_metric(_SCORE_RE, summary)
            comments = self._extract_metric(_COMMENTS_RE, summary)

            posts.append(
                RedditPost(
                    post_id=post_id,
                    subreddit=subreddit,
                    title=title,
                    author=author,
                    score=score,
                    num_comments=comments,
                    created_utc=created_utc,
                    permalink=permalink,
                    url=permalink,
                    is_self=False,
                    over_18=False,
                )
            )

        return posts

    def fetch_hot_posts_for_subreddits(
        self,
        subreddits: Iterable[str],
        limit_per_subreddit: int = 25,
        sleep_seconds: float = 0.0,
    ) -> List[RedditPost]:
        subreddit_list = [item.strip() for item in subreddits if item.strip()]
        combined: List[RedditPost] = []
        for idx, subreddit in enumerate(subreddit_list):
            combined.extend(self.fetch_hot_posts(subreddit=subreddit, limit=limit_per_subreddit))
            if sleep_seconds > 0 and idx < len(subreddit_list) - 1:
                time.sleep(sleep_seconds)
        return combined

    @staticmethod
    def _extract_metric(pattern: re.Pattern, text: str) -> int:
        match = pattern.search(text or "")
        return int(match.group(1)) if match else 0

    @staticmethod
    def _get_text(node: ElementTree.Element, xpath: str) -> str:
        child = node.find(xpath, ATOM_NS)
        return child.text.strip() if child is not None and child.text else ""


def sort_hot_posts(posts: Iterable[RedditPost]) -> List[RedditPost]:
    """Sort posts by score, comments and recency."""
    return sorted(posts, key=lambda p: (p.score, p.num_comments, p.created_utc), reverse=True)
