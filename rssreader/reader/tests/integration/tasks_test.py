import logging
import time
from uuid import UUID
from faker import Faker
from django.test import TransactionTestCase, override_settings
from django.core import mail
from django.contrib.auth.models import User
from celery.contrib.testing.worker import setup_app_for_worker, start_worker
from celery.contrib.testing.app import TestApp
from celery import current_app
from reader.repositories import FeedsRepository
from reader.services import FeedsService
from reader.domain_models import Feed
from reader.tests.factories import FeedFactory
from reader import tasks


faker = Faker()


class TasksTests(TransactionTestCase):
    feed_repo: FeedsRepository
    user: User
    feed: Feed
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        app = TestApp()
        cls.celery_worker = start_worker(app)
        cls.celery_worker.__enter__()
    
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.celery_worker.__exit__(None, None, None)
    
    def setUp(self):
        self.feed_repo = FeedsRepository()

        username = faker.user_name()
        user_password = faker.password()
        user_email = faker.email()
        first_name = faker.first_name()
        last_name = faker.last_name()
        
        self.user = User.objects.create_user(
            username=username,
            email=user_email,
            password=user_password,
            first_name=first_name,
            last_name=last_name
        )
        
        self.feed = self.feed_repo.create_user_feed(
            self.user.id, FeedFactory.build()
        )

        # Monkey patch FeedsService.refresh_feed to simulate failure
        self.tasks = tasks
        def refresh_feed(self, feed_id: UUID) -> Feed:
            raise Exception('Mock feed refresh fail')
        self.tasks.feeds_service.refresh_feed = refresh_feed.__get__(
            self.tasks.feeds_service, FeedsService
        )
        
    @override_settings(
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'
    )
    def test_send_email_notification(self):
        self.tasks.spawn_feed_updates.delay()
        
        time.sleep(10)
        
        self.assertEqual(len(mail.outbox), 1)        
        self.assertEqual(
            mail.outbox[0].subject,
            f'Feed {self.feed.title} failed to update'
        )
        