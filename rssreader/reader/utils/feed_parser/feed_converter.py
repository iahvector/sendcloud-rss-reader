import time
from datetime import datetime
from feedparser import FeedParserDict
from django.utils import timezone
from reader.domain_models import Feed, Item
from reader.exceptions import InvalidRssFeedException


class FeedConverter:
    required_feed_props = ['link', 'updated_parsed']
    required_item_props = ['id', 'link', 'published_parsed']

    data: FeedParserDict
    rss_link: str

    def __init__(self, rss_link: str, data: FeedParserDict):
        self.rss_link = rss_link
        self.data = data

    def _validate(self, segment: FeedParserDict, required_props: list[str]) -> list[str]:
        missing_props = []
        for prop in required_props:
            if prop not in segment:
                missing_props.append(prop)

        return missing_props

    def _validate_feed(self):
        msg = 'Feed is missing {}'
        if 'feed' not in self.data:
            raise InvalidRssFeedException(msg.format('feed data'))

        missing = self._validate(self.data.feed, self.required_feed_props)
        if len(missing) > 0:
            raise InvalidRssFeedException(msg.format(', '.join(missing)))

    def _validate_feed_item(self, item: FeedParserDict):
        msg = 'Feed item is missing {}'
        if 'entries' not in self.data:
            raise InvalidRssFeedException(msg.format('items'))

        missing = self._validate(item, self.required_item_props)
        if len(missing) > 0:
            raise InvalidRssFeedException(msg.format(', '.join(missing)))

    def convert(self) -> Feed:
        items = []
        self._validate_feed()
        for entry in self.data.entries:
            self._validate_feed_item(entry)
            if 'published_parsed' in entry:
                pub_time_struct = entry.published_parsed
            else:
                pub_time_struct = entry.updated_parsed
            
            pub_time = timezone.make_aware(
                datetime.fromtimestamp(time.mktime(pub_time_struct))
            )
            item = Item(
                None,
                entry.id,
                entry.get('title', 'No title'),
                entry.get('description', 'No description'),
                entry.link,
                pub_time,
                False,
                None,
                None
            )
            items.append(item)

        if 'published_parsed' in self.data.feed:
            pub_time_struct = self.data.feed.published_parsed
        else:
            pub_time_struct = self.data.feed.updated_parsed
        
       
        pub_time = timezone.make_aware(
            datetime.fromtimestamp(time.mktime(pub_time_struct))
        ) 
        feed = Feed(
            None,
            self.data.feed.get('title', 'No title'),
            self.data.feed.get('description', 'No description'),
            self.data.feed.link,
            self.rss_link,
            pub_time,
            timezone.now(),
            True,
            items,
            None
        )

        return feed
