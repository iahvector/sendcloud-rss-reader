import factory
from faker import Faker
from datetime import timezone
from reader.domain_models import Feed
from .item_factory import ItemFactory


faker = Faker()


class FeedFactory(factory.Factory):
    class Meta:
        model = Feed

    id = faker.uuid4()
    title =  faker.sentence(nb_words=10, variable_nb_words=True)
    description = faker.paragraph(nb_sentences= 10, variable_nb_sentences = True)
    link = faker.uri()
    rss_link = faker.uri()
    publication_time = faker.date_time(timezone.utc)
    update_time = faker.date_time(timezone.utc)
    is_automatic_update_enabled = True
    items = factory.List(
        factory.SubFactory(ItemFactory) for _ in range(10)
    )
    owner = faker.pyint()
