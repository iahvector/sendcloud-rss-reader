import uuid
from django.db import models
from django.contrib.auth.models import User
from reader.domain_models import Feed as FeedDM

class Feed(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=250)
    description = models.CharField(max_length=3000)
    link = models.URLField()
    rss_link = models.URLField()
    publication_time = models.DateTimeField()
    is_automatic_update_enabled = models.BooleanField(default=True)
    update_time = models.DateTimeField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def to_domain_model(self, with_items: bool = True):
        items = None
        if with_items:
            items = [
                i.to_domain_model() for i in self.item_set.all()
            ] 
        return FeedDM(
            id=self.id,
            title=self.title,
            description=self.description,
            link=self.link,
            rss_link=self.rss_link,
            publication_time=self.publication_time,
            update_time=self.update_time,
            is_automatic_update_enabled=self.is_automatic_update_enabled,
            items=items,
            owner=self.owner.id
        )
        
    def __str__(self):
        return f'{self.title} - {self.link}'
