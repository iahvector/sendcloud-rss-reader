from uuid import UUID
from django.core.mail import send_mail
from celery import Task, shared_task
from celery.utils.log import get_task_logger
from reader.repositories import FeedsRepository
from reader.utils.feed_parser import FeedParser
from reader.services import FeedsService
from users.services import UsersService
from users.repositories import UsersRepository

logger = get_task_logger(__name__)
feeds_repo = FeedsRepository()
parser = FeedParser()
users_repo = UsersRepository()
users_service = UsersService(users_repo)
feeds_service = FeedsService(feeds_repo, parser)

class RefreshFeedTask(Task):
    retry_backoff=True
    autoretry_for=(Exception,)
    max_retries = 3

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        super(RefreshFeedTask, self).on_failure(
            exc, task_id, args, kwargs, einfo
        )
        feed_id = args[0]
        msg = f'Refresh feed {feed_id} task failed with args: {repr(args)}, kwargs: {repr(kwargs)} after {self.request.retries} retries'
        logger.error(msg, exc, einfo)
        feed = feeds_repo.disable_feed_automatic_update(feed_id)
        send_feed_update_failure_email_notification.delay(feed.id)

@shared_task(bind=True, base=RefreshFeedTask)
def refresh_feed(self, feed_id: UUID):
    feeds_service.refresh_feed(feed_id)

@shared_task(bind=True, retry_backoff=True, autoretry_for=(Exception,))
def send_feed_update_failure_email_notification(self, feed_id: UUID):
    feed = feeds_service.get_feed(feed_id)
    owner = users_service.get_user(feed.owner)
    subject = f'Feed {feed.title} failed to update'
    body = f'''
Feed {feed.title} failed to update and automaic update for it has been disabled.
Refresh the feed manually using the API to enable automatic updates again.
'''
    send_mail(
        subject,
        body,
        'i@islamhassan.com',
        [owner.email],
        fail_silently=False,
    )

@shared_task(bind=True, retry_backoff=True, autoretry_for=(Exception,))
def spawn_feed_updates(self):
    page_size = 100
    feeds_count = feeds_repo.get_automatically_updateable_feeds_count()
    for offset in range(0, feeds_count, page_size):
        feeds = feeds_repo.get_automatically_updateable_feeds(offset, page_size)
        for feed in feeds:
            refresh_feed.delay(feed.id)
        