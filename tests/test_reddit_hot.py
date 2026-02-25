import io
import unittest
from unittest.mock import patch

from ingestion.reddit_hot import RedditClient, sort_hot_posts


class FakeResponse:
    def __init__(self, payload: str):
        self._buffer = io.BytesIO(payload.encode("utf-8"))

    def read(self):
        return self._buffer.read()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


XML_PAYLOAD = """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<feed xmlns=\"http://www.w3.org/2005/Atom\">
  <entry>
    <id>t3_abc123</id>
    <title>New coding model benchmark</title>
    <updated>Tue, 11 Mar 2025 09:01:00 GMT</updated>
    <author><name>alice</name></author>
    <content type=\"html\">123 points 45 comments</content>
    <link href=\"https://www.reddit.com/r/MachineLearning/comments/abc123/demo/\"/>
  </entry>
  <entry>
    <id>t3_def456</id>
    <title>Another post</title>
    <updated>Tue, 11 Mar 2025 07:01:00 GMT</updated>
    <author><name>bob</name></author>
    <content type=\"html\">22 points 4 comments</content>
    <link href=\"https://www.reddit.com/r/MachineLearning/comments/def456/demo2/\"/>
  </entry>
</feed>
"""


class RedditHotTests(unittest.TestCase):
    def test_fetch_hot_posts_parses_rss(self):
        with patch("ingestion.reddit_hot.urlopen", return_value=FakeResponse(XML_PAYLOAD)):
            client = RedditClient(user_agent="test-agent")
            posts = client.fetch_hot_posts("MachineLearning", limit=2)

        self.assertEqual(len(posts), 2)
        self.assertEqual(posts[0].post_id, "t3_abc123")
        self.assertEqual(posts[0].score, 123)
        self.assertEqual(posts[0].num_comments, 45)

    def test_sort_hot_posts(self):
        with patch("ingestion.reddit_hot.urlopen", return_value=FakeResponse(XML_PAYLOAD)):
            posts = RedditClient(user_agent="test-agent").fetch_hot_posts("MachineLearning", limit=2)

        ordered = sort_hot_posts(posts)
        self.assertEqual(ordered[0].post_id, "t3_abc123")


if __name__ == "__main__":
    unittest.main()
