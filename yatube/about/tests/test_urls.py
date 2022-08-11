from http import HTTPStatus

from django.test import Client, TestCase


class AboutURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.urls_with_templates = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }

    def setUp(self):
        self.unauthorized_client = Client()

    def test_urls_accessibility_for_all_users(self):
        """Проверка URL-адресов, доступных всем пользователям."""
        for address in AboutURLTest.urls_with_templates.keys():
            with self.subTest(address=address):
                response = self.unauthorized_client.get(address)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK.value,
                    'URL-адрес недоступен всем пользователям'
                )

    def test_urls_use_correct_templates(self):
        """Проверка использования URL-адресом соответствующего шаблона."""
        for address, template in AboutURLTest.urls_with_templates.items():
            with self.subTest(address=address):
                response = self.unauthorized_client.get(address)
                self.assertTemplateUsed(
                    response,
                    template,
                    'URL-адрес использует неверный шаблон'
                )
