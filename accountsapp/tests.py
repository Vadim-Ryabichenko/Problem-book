from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from .serializers import UserSerializer




class RegisterViewTest(TestCase):
    def setUp(self):
        self.register_url = reverse('register_page')
        self.register_data = {
            'username': 'loma',
            'email': 'loma@example.com',
            'first_name': 'Lom',
            'last_name': 'Krotov',
            'password1': 'lomapassword',
            'password2': 'lomapassword',
        }

    def test_register(self):
        response = self.client.post(self.register_url, self.register_data)
        self.assertEqual(response.status_code, 302) 
        self.assertRedirects(response, reverse('register_done'))
        self.assertTrue(User.objects.filter(username=self.register_data['username']).exists())


class LoginTest(TestCase):
    def setUp(self):
        self.username = 'yupi'
        self.password = 'yupipassword'
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.login_url = reverse('login_page')

    def test_login_successful(self):
        response = self.client.post(self.login_url, {'username': self.username, 'password': self.password})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertRedirects(response, reverse('login_done'))


class LogoutViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='donald', password='krakra1999')

    def test_logout_view(self):
        self.client.login(username='donald', password='krakra1999')
        self.assertTrue(self.client.session.get('_auth_user_id'))
        logout_url = reverse('logout_page')
        response = self.client.get(logout_url)
        self.assertFalse(response.context['user'].is_authenticated)


class UserModelViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_data = {'username': 'testuser', 'password': 'testpassword'}
        self.user = User.objects.create_user(**self.user_data)

    def test_list_users(self):
        response = self.client.get('/accounts/api/users/') 
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_user(self):
        new_user_data = {'username': 'newuser', 'password': 'newpassword'}
        response = self.client.post('/accounts/api/users/', data=new_user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_user = User.objects.get(username=new_user_data['username'])
        self.assertIsNotNone(new_user)
        self.assertEqual(new_user.username, new_user_data['username'])

    def test_retrieve_user(self):
        response = self.client.get(f'/accounts/api/users/{self.user.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_user(self):
        updated_data = {'username': 'newusername', 'password': 'newpassword'}
        response = self.client.put(f'/accounts/api/users/{self.user.id}/', data=updated_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, updated_data['username'])

    def test_delete_user(self):
        response = self.client.delete(f'/accounts/api/users/{self.user.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(User.DoesNotExist):
            self.user.refresh_from_db()


class UserSerializerTest(TestCase):

    def test_create_user(self):
        user_data = {
            'username': 'Hiper',
            'email': 'hiper@example.com',
            'first_name': 'Hip',
            'last_name': 'Super',
            'password': 'hiperpassword'
        }
        serializer = UserSerializer(data=user_data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.username, user_data['username'])
        self.assertEqual(user.email, user_data['email'])
        self.assertEqual(user.first_name, user_data['first_name'])
        self.assertEqual(user.last_name, user_data['last_name'])
        print(user.id)
        self.assertIsNotNone(user.id)
 


