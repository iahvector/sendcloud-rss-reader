import feedparser
from reader.domain_models import Feed
from .feed_converter import FeedConverter


class FeedParser:
    def parse(self, url: str) -> Feed:
        data = feedparser.parse(url)
        return FeedConverter(url, data).convert()