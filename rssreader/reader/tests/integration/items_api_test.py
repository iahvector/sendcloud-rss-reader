from faker import Faker
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from reader.repositories import FeedsRepository, ItemsRepository
from reader.tests.factories import FeedFactory


faker = Faker()


class ItemsApiTests(APITestCase):
    feed_repo: FeedsRepository
    items_repo: ItemsRepository

    user: User
    username: str
    user_password: str
    user_email: str
    
    def setUp(self):
        self.feed_repo = FeedsRepository()
        self.items_repo = ItemsRepository()

        self.username = faker.user_name()
        self.user_password = faker.password()
        self.user_email = faker.email()
        self.user = User.objects.create_user(
            self.username, self.user_email, self.user_password
        )
        
        self.client.force_authenticate(user=self.user)

    def test_list_user_items(self):
        feeds_count = 3
        feeds = [
            self.feed_repo.create_user_feed(self.user.id, FeedFactory.build()) \
            for _ in range(feeds_count)
        ]
        
        items_count = 0
        user1_items_ids = set()
        for feed in feeds:
            items_count += len(feed.items)
            for item in feed.items:
                user1_items_ids.add(str(item.id))

        username2 = faker.user_name()
        user_password2 = faker.password()
        user_email2 = faker.email()
        user2 = User.objects.create_user(
            username2, user_email2, user_password2
        )

        feeds2 = [
            self.feed_repo.create_user_feed(user2.id, FeedFactory.build()) \
            for _ in range(feeds_count)
        ]

        user2_items_ids = set()
        for feed in feeds2:
            for item in feed.items:
                user2_items_ids.add(str(item.id))
        
        api_url = f'/api/rss/items/'
        res = self.client.get(api_url)
        self.assertEqual(res.status_code, 200)
        result_count = res.data.get('count')
        results = res.data.get('results')
        self.assertEqual(len(results), items_count)
        self.assertEqual(result_count, items_count)

        for item in results:
            id = item.get('id')
            self.assertTrue(id in user1_items_ids)
            self.assertFalse(id in user2_items_ids)
    
    def test_list_user_unread_items(self):
        feeds_count = 3
        feeds = [
            self.feed_repo.create_user_feed(self.user.id, FeedFactory.build()) \
            for _ in range(feeds_count)
        ]
        
        items_count = 0
        for feed in feeds:
            items_count += len(feed.items)
        
        for feed in feeds:
            self.items_repo.mark_user_item_as_read(
                self.user.id, feed.items[0].id, True
            )
        
        api_url = f'/api/rss/items/?unread_only=true'
        res = self.client.get(api_url)
        self.assertEqual(res.status_code, 200)
        result_count = res.data.get('count')
        results = res.data.get('results')
        expected_count = items_count - 3
        self.assertEqual(len(results), expected_count)
        self.assertEqual(result_count, expected_count)

        for item in results:
            self.assertFalse(item.get('is_read'))
    
    def test_mark_item_as_read(self):
        feed = self.feed_repo.create_user_feed(
            self.user.id, FeedFactory.build()
        )

        item = feed.items[0]
        self.assertFalse(item.is_read)
        
        api_url = f'/api/rss/items/{item.id}/mark_as_read/'
        body = {"is_read": True}
        res = self.client.patch(api_url, body)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data.get('id'), str(item.id))
        self.assertTrue(res.data.get('is_read'))

        item = self.items_repo.get_user_item(self.user.id, item.id)
        self.assertTrue(item.is_read)
    
    def test_mark_item_as_unread(self):
        feed = self.feed_repo.create_user_feed(
            self.user.id, FeedFactory.build()
        )

        item = feed.items[0]
        self.items_repo.mark_user_item_as_read(self.user.id, item.id, False)
        
        api_url = f'/api/rss/items/{item.id}/mark_as_read/'
        body = {"is_read": False}
        res = self.client.patch(api_url, body)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data.get('id'), str(item.id))
        self.assertFalse(res.data.get('is_read'))

        item = self.items_repo.get_user_item(self.user.id, item.id)
        self.assertFalse(item.is_read)
    
    def test_mark_non_existing_item_as_read(self):
        api_url = f'/api/rss/items/{faker.uuid4()}/mark_as_read/'
        body = {"is_read": True}
        res = self.client.patch(api_url, body)
        self.assertEqual(res.status_code, 404)
        error_code = res.data['errors'][0]['code']
        self.assertEqual(error_code, 'item_not_found')