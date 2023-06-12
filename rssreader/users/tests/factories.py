import factory
from faker import Faker
from users.domain_models import User


faker = Faker()


class UserFactory(factory.Factory):
    class Meta:
        model = User

    id = faker.pyint(min_value=0)
    username = faker.user_name()
    email = faker.email()
    first_name = faker.first_name()
    last_name = faker.last_name()