from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class UsersURLTest(TestCase):
    def setUp(self):
        self.unauthorized_client = Client()

        self.user = User.objects.create_user(username='Test user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_accessibility_for_all_users(self):
        """Проверка URL-адресов, доступных всем пользователям."""
        urls_for_all = [
            '/auth/signup/',
            '/auth/login/',
            '/auth/password_reset/',
            '/auth/password_reset/done/',
            '/auth/reset/<uidb64>/<token>/',
            '/auth/reset/done/',
            '/auth/logout/',
        ]
        for address in urls_for_all:
            with self.subTest(address=address):
                response = self.unauthorized_client.get(address)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK.value,
                    'URL-адрес недоступен всем пользователям'
                )

    def test_urls_accessibility_for_authorized_users(self):
        """Проверка URL-адресов,
        доступных только авторизованным пользователям.
        """
        urls_for_authorized = [
            '/auth/password_change/',
            '/auth/password_change/done/',
        ]
        for address in urls_for_authorized:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK.value,
                    'URL-адрес недоступен для авторизованного пользователя'
                )

    def test_urls_use_correct_templates(self):
        """Проверка использования URL-адресом соответствующего шаблона."""
        urls_templates = {
            '/auth/signup/': 'users/signup.html',
            '/auth/login/': 'users/login.html',
            '/auth/password_reset/': 'users/password_reset_form.html',
            '/auth/password_reset/done/': 'users/password_reset_done.html',
            '/auth/reset/<uidb64>/<token>/': ('users/'
                                              'password_reset_confirm.html'),
            '/auth/reset/done/': 'users/password_reset_complete.html',
            '/auth/password_change/': 'users/password_change_form.html',
            '/auth/password_change/done/': 'users/password_change_done.html',
            '/auth/logout/': 'users/logged_out.html',
        }
        for address, template in urls_templates.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(
                    response,
                    template,
                    'URL-адрес использует неверный шаблон'
                )
