from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class UserViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='Test user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_use_correct_templates(self):
        """Проверка использования страницами соответствующего шаблона."""
        page_templates = {
            reverse('users:signup'): 'users/signup.html',
            reverse('users:login'): 'users/login.html',
            reverse('users:password_reset'): 'users/password_reset_form.html',
            reverse('users:password_reset_done'):
                   ('users/password_reset_done.html'),
            reverse('users:password_reset_confirm', args=['uidb64', 'token']):
                   ('users/password_reset_confirm.html'),
            reverse('users:password_reset_complete'):
                   ('users/password_reset_complete.html'),
            reverse('users:password_change'):
                   ('users/password_change_form.html'),
            reverse('users:password_change_done'):
                   ('users/password_change_done.html'),
            reverse('users:logout'): 'users/logged_out.html',
        }
        for reverse_name, template in page_templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(
                    response,
                    template,
                    'Страница использует неверный шаблон'
                )

    def test_signup_page_uses_correct_context_form(self):
        """Проверка типов полей формы, используемой на странице регистрации."""
        page_with_custom_form = [
            reverse('users:signup'),
        ]
        user_form_fields = {
            'first_name': forms.fields.CharField,
            'last_name': forms.fields.CharField,
            'username': forms.fields.CharField,
            'email': forms.fields.EmailField,
        }
        for reverse_name in page_with_custom_form:
            for value, expected_field in user_form_fields.items():
                with self.subTest(value=value):
                    response = self.authorized_client.get(reverse_name)
                    form_all_fields = response.context.get('form').fields
                    current_field = form_all_fields.get(value)
                    self.assertIsInstance(
                        current_field,
                        expected_field,
                        'Тип поля формы не соответствует ожидаемому'
                    )
