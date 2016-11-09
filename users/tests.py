from django.test import TestCase, Client
from django.contrib.auth.models import User


class LoginTestCase(TestCase):
    def setUp(self):
        pass

    def _create_user(self, username, email, password):
        user, created = User.objects.get_or_create(username=username)
        user.set_password(password)
        user.email = email
        user.is_active = True
        user.save()

        return user

    def _login(self, username, email, password):
        client = Client()
        assert client.login(username=username, email=email, password=password)
        return client

    def _logout(self, client=None):
        if not client:
            client = self.client
        client.logout()

    def _create_user_and_login(self, username="bob", email="bob@fs.com", password="bob"):
        self.login_username = username
        self.login_password = password
        self.user = self._create_user(username, email, password)
        self.client = self._login(username, email, password)
        self.anon = Client()

    def test_login_with_username(self):
        user = self._create_user('aaaaaa', 'aaaaaa@fs.com', '123456')
        client = Client()
        response = client.post('/users/login/', {'username': user.username, 'password': '123456'})
        self.assertEqual(response.templates[0].name, "registration/login.html")

    def test_bad_login(self):
        """Login Fails"""
        client = Client()
        response = client.post('/users/login/', {'email': 'john@fs.com', 'password': 'smith'})
        self.assertEqual(response.templates[0].name, "registration/login.html")

    def test_login(self):
        """Login Success"""
        user = self._create_user('john', 'lennon@thebeatles.com', '123456')
        client = self._login(user.username, user.email,"123456")
        self.client.get('/accounts/logout/')

    def test_koboform(self):
        "KOboform Page After Sucessfull Login "
        user = self._create_user('john', 'lennon@thebeatles.com', '123456')
        response = self.client.post('/users/login/', {'email': user.email, 'password': '123456'})
        self.assertEqual(response.content, "")
        kobo = self.client.get('/')
        self.assertEqual(kobo.status_code, 200)
        self.client.get('/accounts/logout/')

    def test_koboform_without_login(self):
        "Redirects to login "
        self.client.get('/accounts/logout/')
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)

