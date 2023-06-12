import uuid
from django.test import SimpleTestCase
from reader.tests.mocks import FeedParserMock, FeedRepositoryMock
from reader.services import FeedsService
from reader.domain_models import Feed

class FeedsServiceTest(SimpleTestCase):
    def test_follow_feed(self):
         repo = FeedRepositoryMock()
         parser = FeedParserMock()
         service = FeedsService(repo, parser)

         url = 'https://random.url/rss'
         user_id = uuid.uuid4()

         feed = service.follow_feed(user_id, url)
         self.assertIsInstance(feed, Feed)
         self.assertEqual(url, feed.rss_link)
         self.assertEqual(user_id, feed.owner)
