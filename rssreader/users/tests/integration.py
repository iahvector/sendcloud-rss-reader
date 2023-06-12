from faker import Faker
from rest_framework.test import APITestCase
from users.tests.factories import UserFactory
from django.contrib.auth.models import User


faker = Faker()


class UsersApiTests(APITestCase):
    def test_signup(self):
        user = UserFactory.build()
        password = faker.password()
        api_url = '/api/users/'
        body = {
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'password': password
        }
        
        res = self.client.post(api_url, body)
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.data.get('username'), user.username)
        self.assertEqual(res.data.get('email'), user.email)
        self.assertEqual(res.data.get('first_name'), user.first_name)
        self.assertEqual(res.data.get('last_name'), user.last_name)
        
        user_db = User.objects.get(email=user.email)
        self.assertEqual(user_db.id, res.data['id'])
    
    def test_signup_existing_user(self):
        user = UserFactory.build()
        password = faker.password()
        api_url = '/api/users/'
        body = {
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'password': password
        }
        
        res = self.client.post(api_url, body)
        res = self.client.post(api_url, body)
        self.assertEqual(res.status_code, 400)
        error_code = res.data['errors'][0]['code']
        self.assertEqual(error_code, 'user_already_exists')
