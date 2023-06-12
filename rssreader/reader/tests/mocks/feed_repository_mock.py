import uuid
from reader.domain_models import Feed

class FeedRepositoryMock:
    _db: dict[uuid.UUID, Feed] = {}

    def check_user_feed_exists_by_link(
        self, user_id: uuid.UUID, rss_link: str
    ) -> bool:
        for feed in self._db.values():
            if feed.rss_link == rss_link and feed.owner == user_id:
                return True
        return False
    
    def create_user_feed(self, user_id: uuid.UUID, feed: Feed) -> Feed:
        feed.id = uuid.uuid4()
        feed.owner = user_id
        self._db[feed.id] = feed
        return feed