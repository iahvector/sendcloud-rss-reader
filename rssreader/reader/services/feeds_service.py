from uuid import UUID
from reader.repositories import FeedsRepository
from reader.domain_models import Feed
from reader.utils.feed_parser import FeedParser
from reader.exceptions import FeedAlreadyExistsException


class FeedsService:
    feeds_repo: FeedsRepository
    
    parser: FeedParser

    def __init__(
        self,
        feeds_repo: FeedsRepository,
        parser: FeedParser,
    ):
        self.feeds_repo = feeds_repo
        self.parser = parser

    def get_feed(self, feed_id: UUID) -> Feed:
        return self.feeds_repo.get_feed(feed_id)

    def _get_user_feed_by_id(
        self, user_id: int, feed_id: UUID, unread_items_only: bool = False
    ) -> Feed:
        return self.feeds_repo.get_user_feed(
            user_id, feed_id, unread_items_only
        )

    def follow_feed(self, user_id: int, rss_link: str) -> Feed:
        if self.feeds_repo.check_user_feed_exists_by_link(user_id, rss_link):
            msg = f'Feed {rss_link} already exists'
            raise FeedAlreadyExistsException(msg)

        feed = self.parser.parse(rss_link)
        return self.feeds_repo.create_user_feed(user_id, feed)
    
    def unfollow_feed(self, user_id: int, feed_id: UUID):
        self.feeds_repo.delete_user_feed(user_id, feed_id)

    def refresh_feed(self, feed_id: UUID) -> Feed:
        f = self.get_feed(feed_id)
        feed = self.parser.parse(f.rss_link)
        return self.feeds_repo.refresh_feed(feed_id, feed)

    def refresh_user_feed(self, user_id: int, feed_id: UUID) -> Feed:
        f = self._get_user_feed_by_id(user_id, feed_id)

        feed = self.parser.parse(f.rss_link)

        feed = self.feeds_repo.refresh_user_feed(user_id, feed_id, feed)
        if not feed.is_automatic_update_enabled:
            feed = self.feeds_repo.enable_feed_automatic_update(user_id, feed_id)
        
        return feed

    def get_user_feed_by_id(
        self, user_id: int, feed_id: UUID, unread_items_only: bool = False
    ):
        return self._get_user_feed_by_id(user_id, feed_id, unread_items_only)

    def get_user_feeds(
        self, user_id: int, page: int = 0, page_size: int = 100
    ) -> tuple[list[Feed], int]:
        offset = page * page_size
        return self.feeds_repo.get_all_user_feeds(user_id, offset, page_size)
    
    def disable_feed_automatic_update(self, feed_id: UUID) -> Feed:
        return self.feeds_repo.disable_feed_automatic_update(feed_id)
