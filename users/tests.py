from django.test import TestCase, Client
from django.contrib.auth.models import User


class LoginTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_login_with_username(self):
        user = User.objects.create_user('aaaaaa', 'aaaaaa@fs.com', '123456')
        user.is_active = True
        user.save()
        response = self.client.post('/users/login/', {'username': 'aaaaaa', 'password': '123456'})
        self.assertEqual(response.templates[0].name, "registration/login.html")

    def test_bad_login(self):
        """Login Fails"""
        response = self.client.post('/users/login/', {'email': 'john@fs.com', 'password': 'smith'})
        self.assertEqual(response.templates[0].name, "registration/login.html")

    def test_login(self):
        """Login Success"""
        user = User.objects.create_user('john', 'lennon@thebeatles.com', '123456')
        user.is_active = True
        user.save()
        response = self.client.post('/users/login/', {'email': user.email, 'password': '123456'})
        self.assertEqual(response.content, "")
        self.client.get('/accounts/logout/')

    def test_koboform(self):
        "KOboform Page After Sucessfull Login "
        user = User.objects.create_user('john', 'lennon@thebeatles.com', '123456')
        user.is_active = True
        user.save()
        response = self.client.post('/users/login/', {'email': 'lennon@thebeatles.com', 'password': '123456'})
        self.assertEqual(response.content, "")
        kobo = self.client.get('/')
        self.assertEqual(kobo.status_code, 200)
        self.client.get('/accounts/logout/')

    def test_koboform_without_login(self):
        "Redirects to login "
        self.client.get('/accounts/logout/')
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)

