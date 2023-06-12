from uuid import UUID
from django.db import transaction
from django.contrib.auth.models import User
from django.db.models import Prefetch
from django.utils import timezone
from reader.domain_models import Feed as FeedDM
from reader.models import Feed, Item
from reader.exceptions import FeedNotFoundException


class FeedsRepository:

    @transaction.atomic
    def create_user_feed(self, user_id: int, feed: FeedDM) -> FeedDM:
        feed_db = Feed.objects.create(
            title=feed.title,
            description=feed.description,
            link=feed.link,
            rss_link=feed.rss_link,
            publication_time=feed.publication_time,
            update_time=feed.update_time,
            owner=User(id=user_id)
        )

        items = []
        for i in feed.items:
            items.append(
                Item(
                    guid=i.guid,
                    title=i.title,
                    description=i.description,
                    link=i.link,
                    publication_time=i.publication_time,
                    is_read=i.is_read,
                    feed=feed_db,
                    owner=User(id=user_id)
                )
            )
        Item.objects.bulk_create(items)

        feed_db.refresh_from_db()
        return feed_db.to_domain_model()

    def check_user_feed_exists_by_link(
        self, user_id: int, rss_link: str
    ) -> bool:
        return Feed.objects.filter(
            owner=User(user_id), rss_link=rss_link
        ).exists()

    def get_automatically_updateable_feeds_count(self) -> int:
        return Feed.objects.filter(is_automatic_update_enabled=True).count()

    def get_automatically_updateable_feeds(
        self, offset: int = 0, limit: int = 100
    ) -> list[FeedDM]:
        feeds = Feed.objects.filter(is_automatic_update_enabled=True)
        return [feed.to_domain_model() for feed in feeds[offset:offset+limit]]
    
    def disable_feed_automatic_update(
        self, feed_id: UUID
    ) -> FeedDM:
        try:
            feed_db = Feed.objects.get(id=feed_id)
        except Feed.DoesNotExist as e:
            msg = f'Feed {feed_id} not found'
            raise FeedNotFoundException(msg)
            
        feed_db.is_automatic_update_enabled = True
        feed_db.save()
        return feed_db.to_domain_model()
    
    def enable_feed_automatic_update(
        self, user_id: int, feed_id: UUID
    ) -> FeedDM:
        try:
            feed_db = Feed.objects.get(id=feed_id, owner=User(id=user_id))
        except Feed.DoesNotExist as e:
            msg = f'Feed {feed_id} not found'
            raise FeedNotFoundException(msg)
            
        feed_db.is_automatic_update_enabled = True
        feed_db.save()
        return feed_db.to_domain_model()

    def get_all_user_feeds(
        self, user_id: int, offset: int = 0, limit: int = 100
    ) -> tuple[list[FeedDM], int]:
        feeds = Feed.objects.filter(owner=User(id=user_id))
        feed_count = feeds.count()
        return ([
            f.to_domain_model(with_items=False)
            for f in feeds[offset:offset+limit]
        ], feed_count)
    
    def _get_feed(self, feed_id: UUID, user_id: int | None = None) -> Feed:
        try:
            feed = Feed.objects.filter(id=feed_id)
            if user_id is not None:
                feed.filter(owner=User(id=user_id))

            return feed.get()
        except Feed.DoesNotExist as e:
            msg = f'Feed {feed_id} not found'
            raise FeedNotFoundException(msg)

    def get_feed(self, feed_id: UUID) -> FeedDM:
        return self._get_feed(feed_id).to_domain_model()

    def get_user_feed(
        self, user_id: int, feed_id: UUID, unread_items_only: bool = False
    ) -> FeedDM:
        feed = Feed.objects.filter(id=feed_id, owner=User(id=user_id))
        if unread_items_only:
            read_items_qs = Item.objects.filter(is_read=False)
            prefetch = Prefetch('item_set', queryset=read_items_qs)
            feed = feed.prefetch_related(prefetch)

        try:
            return feed.get().to_domain_model()
        except Feed.DoesNotExist as e:
            msg = f'Feed {feed_id} not found'
            raise FeedNotFoundException(msg)

    def refresh_user_feed(
        self, user_id: int, feed_id: UUID, feed: FeedDM
    ) -> FeedDM:
        feed_db = self._get_feed(feed_id, user_id)
        return self._refresh_feed(feed_db, feed)

    def refresh_feed(self, feed_id: UUID, feed: FeedDM) -> FeedDM:
        feed_db = self._get_feed(feed_id)
        return self._refresh_feed(feed_db, feed)

    @transaction.atomic
    def _refresh_feed(self, feed_db: Feed, feed: FeedDM):
        feed_db.title = feed.title
        feed_db.description = feed.description
        feed_db.publication_time = feed.publication_time
        feed_db.update_time = timezone.now()
        feed_db.save()

        guids = set(i.guid for i in feed.items)
        existing_items = {
            i.guid: i for i in Item.objects.filter(feed=feed_db, guid__in=guids)
        }
        guids_to_create = set(
            i for i in guids if i not in existing_items.keys())

        items_to_update = []
        items_to_create = []
        for item in feed.items:
            if item.guid in guids_to_create:
                items_to_create.append(Item(
                    guid=item.guid,
                    description=item.description,
                    link=item.link,
                    publication_time=item.publication_time,
                    is_read=item.is_read,
                    feed=feed_db,
                    owner=feed_db.owner,
                ))
            else:
                item_db = existing_items[item.guid]
                item_db.title = item.title
                item_db.description = item.description
                item_db.link = item.link
                item_db.publication_time = item.publication_time
                items_to_update.append(item_db)
        Item.objects.bulk_create(items_to_create, batch_size=100)
        Item.objects.bulk_update(
            items_to_update,
            ['title', 'description', 'link', 'publication_time'],
            batch_size=100
        )

        feed_db.refresh_from_db()
        return feed_db.to_domain_model()

    def delete_user_feed(self, user_id: int, feed_id: UUID):
        try:
            feed = Feed.objects.get(id=feed_id, owner=User(id=user_id))
        except Feed.DoesNotExist as e:
            msg = f'Feed {feed_id} not found'
            raise FeedNotFoundException(msg)
        
        feed.delete()