from factory import Factory
from faker import Faker
from datetime import timezone
from reader.domain_models import Item

faker = Faker()

class ItemFactory(Factory):
    class Meta:
        model = Item

    id = faker.uuid4()
    guid = faker.uuid4()
    title =  faker.sentence(nb_words=10, variable_nb_words=True)
    description = faker.paragraph(nb_sentences= 10, variable_nb_sentences = True)
    link = faker.uri()
    publication_time = faker.date_time(timezone.utc)
    is_read = False
    feed = faker.uuid4()
    owner = faker.uuid4()