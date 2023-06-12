import uuid
from django.db import models
from django.contrib.auth.models import User
from reader.domain_models import Item as ItemDM
from .feed import Feed


class Item(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    guid = models.CharField(max_length=250, blank=False)
    title = models.CharField(max_length=250, blank=False)
    description = models.CharField(max_length=3000, blank=True)
    link = models.URLField(blank=False)
    publication_time = models.DateTimeField(blank=False)
    is_read = models.BooleanField(default=False)
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def to_domain_model(self) -> ItemDM:
        return ItemDM(
            id=self.id,
            guid=self.guid,
            title=self.title,
            description=self.description,
            link=self.link,
            publication_time=self.publication_time,
            is_read=self.is_read,
            feed=self.feed.id,
            owner=self.owner.id
        )

    def __str__(self):
        return f'{self.title} - {self.link}'
