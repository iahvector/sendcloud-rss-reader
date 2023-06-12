from reader.tests.factories import FeedFactory
from reader.domain_models import Feed


class FeedParserMock:
    def parse(self, url: str) -> Feed:
        return FeedFactory.build(rss_link=url)
