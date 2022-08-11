from django.test import Client, TestCase
from django.urls import reverse


class AboutViewTest(TestCase):
    def setUp(self):
        self.unauthorized_client = Client()

    def test_pages_use_correct_templates(self):
        """Проверка использования страницами соответствующего шаблона."""
        page_templates = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html',
        }
        for reverse_name, template in page_templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.unauthorized_client.get(reverse_name)
                self.assertTemplateUsed(
                    response,
                    template,
                    'Страница использует неверный шаблон'
                )
