from http import HTTPStatus

from django.test import Client, TestCase


class CoreURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.unexisting_url = '/unexisting_page/'

    def setUp(self):
        self.unauthorized_client = Client()

    def test_url_does_not_exist(self):
        """Проверка возврата кода 404 для несуществующего URL-адреса."""
        response = self.unauthorized_client.get(CoreURLTest.unexisting_url)
        self.assertEqual(
            response.status_code,
            HTTPStatus.NOT_FOUND.value,
            'Несуществующий URL-адрес не возвращает код 404'
        )

    def test_url_uses_correct_template(self):
        """Проверка использования несуществующим URL-адресом
        соответствующего шаблона."""
        url_template = 'core/404.html'
        response = self.unauthorized_client.get(CoreURLTest.unexisting_url)
        self.assertTemplateUsed(
            response,
            url_template,
            'URL-адрес использует неверный шаблон'
        )
