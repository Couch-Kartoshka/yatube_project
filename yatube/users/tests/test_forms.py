from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class UserFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')

    def setUp(self):
        self.unauthorized_client = Client()

    def test_signup(self):
        """Проверка создания валидной формой нового пользователя в БД."""
        users_count = User.objects.count()
        form_data = {
            'first_name': 'Testfirstname',
            'last_name': 'Testlastname',
            'username': 'testuser',
            'email': 'testuser@email.com',
            'password1': 'qWoldk578sN',
            'password2': 'qWoldk578sN',
        }
        response = self.unauthorized_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:index'),
            msg_prefix='Редирект на главную страницу не работает',
        )
        self.assertEqual(
            User.objects.count(),
            users_count + 1,
            'Количество записей в БД не увеличивается',
        )
        self.assertTrue(
            User.objects.filter(
                first_name='Testfirstname',
                last_name='Testlastname',
                username='testuser',
                email='testuser@email.com',
            ).exists(),
            'Новый пользователь не был добавлен в БД',
        )
