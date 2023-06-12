from faker import Faker
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from reader.repositories import FeedsRepository, ItemsRepository
from reader.tests.factories import FeedFactory
from reader.exceptions import FeedNotFoundException


faker = Faker()


class FeedsApiTests(APITestCase):
    feed_repo: FeedsRepository
    items_repo: ItemsRepository

    user: User
    username: str
    user_password: str
    user_email: str

    test_feed_url = 'https://lorem-rss.herokuapp.com/feed'

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
        
    def test_follow_feed(self):
        api_url = '/api/rss/feeds/'
        body = {
            'url': self.test_feed_url
        }
        res = self.client.post(api_url, body)
        self.assertEqual(res.status_code, 201)

        res_body = res.data
        self.assertEqual(res_body.get('rss_link'), self.test_feed_url)
        
        feed_id = res_body.get('id')

        feed = self.feed_repo.get_feed(feed_id)
        self.assertEqual(feed.title, res_body.get('title'))
        self.assertEqual(len(feed.items), len(res_body.get('items')))
    
    def test_follow_existing_feed_for_same_user(self):
        api_url = '/api/rss/feeds/'
        body = {
            'url': self.test_feed_url
        }
        self.client.post(api_url, body) 
        res = self.client.post(api_url, body) 
        self.assertEqual(res.status_code, 400)
        error_code = res.data['errors'][0]['code']
        self.assertEqual(error_code, 'feed_already_exists')

    def test_follow_existing_feed_different_user(self):
        api_url = '/api/rss/feeds/'
        body = {
            'url': self.test_feed_url
        }
        res = self.client.post(api_url, body) 
        self.assertEqual(res.status_code, 201)

        username2 = faker.user_name()
        user_password2 = faker.password()
        user_email2 = faker.email()
        user2 = User.objects.create_user(
            username2, user_email2, user_password2
        )
        
        self.client.force_authenticate(user=user2)
        res = self.client.post(api_url, body) 
        self.assertEqual(res.status_code, 201)
    
    def test_refesh_feed(self):
        feed = self.feed_repo.create_user_feed(
            self.user.id, FeedFactory.build(rss_link=self.test_feed_url)
        )
        api_url = f'/api/rss/feeds/{feed.id}/refresh/'
        res = self.client.post(api_url) 
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['id'], str(feed.id))
    
    def test_refresh_non_existing_feed(self):
        api_url = f'/api/rss/feeds/{faker.uuid4()}/refresh/'
        res = self.client.post(api_url) 
        self.assertEqual(res.status_code, 404)
        error_code = res.data['errors'][0]['code']
        self.assertEqual(error_code, 'feed_not_found')
        
    
    def test_get_feed(self):
        feed = self.feed_repo.create_user_feed(
            self.user.id, FeedFactory.build()
        )
        api_url = f'/api/rss/feeds/{feed.id}/'

        res = self.client.get(api_url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data.get('id'), str(feed.id))
        self.assertEqual(res.data.get('title'), feed.title)
    
    def test_get_feed_unread_items_only(self):
        feed = self.feed_repo.create_user_feed(
            self.user.id, FeedFactory.build()
        )
        self.items_repo.mark_user_item_as_read(
            self.user.id, feed.items[0].id, True
        )
        
        api_url = f'/api/rss/feeds/{feed.id}/?unread_only=true'

        res = self.client.get(api_url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data.get('id'), str(feed.id))
        self.assertEqual(len(res.data.get('items')), len(feed.items) - 1)
        for item in res.data.get('items'):
            self.assertFalse(item.get('is_read'))
        
    
    def test_get_non_existing_feed(self):
        api_url = f'/api/rss/feeds/{faker.uuid4()}/'

        res = self.client.get(api_url)
        self.assertEqual(res.status_code, 404)
        error_code = res.data['errors'][0]['code']
        self.assertEqual(error_code, 'feed_not_found')
        
    
    def test_list_user_feeds(self):
        feeds_count = 10
        feeds = [
            self.feed_repo.create_user_feed(self.user.id, FeedFactory.build())
            for _ in range(feeds_count)
        ]
        
        user1_feeds_ids = {str(feed.id) for feed in feeds}

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

        user2_feeds_ids = {str(feed.id) for feed in feeds2}

        api_url = f'/api/rss/feeds/'
        res = self.client.get(api_url)
        self.assertEqual(res.status_code, 200)
        result_count = res.data.get('count')
        results = res.data.get('results')
        self.assertEqual(len(results), feeds_count)
        self.assertEqual(result_count, feeds_count)

        for feed in results:
            id = feed.get('id')
            self.assertTrue(id in user1_feeds_ids)
            self.assertFalse(id in user2_feeds_ids)
    
    def test_unfollow_feed(self):
        feed = self.feed_repo.create_user_feed(
            self.user.id, FeedFactory.build()
        )

        api_url = f'/api/rss/feeds/{feed.id}/'
        res = self.client.delete(api_url)
        self.assertEqual(res.status_code, 200)

        self.assertRaises(
            FeedNotFoundException, self.feed_repo.get_feed, feed.id
        )

    def test_unfollow_non_existing_feed(self):
        api_url = f'/api/rss/feeds/{faker.uuid4()}/'
        res = self.client.delete(api_url)
        self.assertEqual(res.status_code, 404)
        error_code = res.data['errors'][0]['code']
        self.assertEqual(error_code, 'feed_not_found')

