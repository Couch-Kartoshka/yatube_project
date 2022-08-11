from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from posts.models import Comment, Group, Post

User = get_user_model()


class PostURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст поста',
            author=cls.author
        )
        cls.comment = Comment.objects.create(
            post=PostURLTest.post,
            text='Тестовый текст комментария к посту',
            author=PostURLTest.author
        )
        cls.urls_for_all = (
            '',
            f'/group/{cls.group.slug}/',
            f'/profile/{cls.author.username}/',
            f'/posts/{cls.post.id}/',
        )
        cls.urls_for_authorized_wo_redirection = (
            '/create/',
            '/follow/',
        )
        cls.urls_for_authorized_w_redirection = (
            f'/posts/{cls.post.id}/comment/',
            f'/profile/{cls.author.username}/follow/',
            f'/profile/{cls.author.username}/unfollow/',
        )
        cls.urls_for_post_authors_wo_redirection = (
            f'/posts/{cls.post.id}/edit/',
        )
        cls.urls_for_post_authors_w_redirection = (
            f'/posts/{cls.post.id}/delete/',
        )
        cls.urls_for_comment_authors = (
            f'/comments/{cls.comment.id}/delete/',
        )

    def setUp(self):
        self.unauthorized_client = Client()

        self.user = User.objects.create_user(username='Test user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.authorized_author = Client()
        self.authorized_author.force_login(PostURLTest.author)

    def test_urls_accessibility_for_all_users(self):
        """Проверка URL-адресов, доступных всем пользователям."""
        for address in PostURLTest.urls_for_all:
            with self.subTest(address=address):
                response = self.unauthorized_client.get(address)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK.value,
                    'URL-адрес недоступен всем пользователям'
                )

    def test_urls_accessibility_wo_redirection_for_authorized(self):
        """Проверка URL-адресов без дефолтного редиректа,
        доступных только авторизованным пользователям.
        """
        for address in PostURLTest.urls_for_authorized_wo_redirection:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK.value,
                    'URL-адрес недоступен для авторизованного пользователя'
                )

    def test_urls_accessibility_w_redirection_for_authorized(self):
        """Проверка URL-адресов с дефолтным редиректом,
        доступных только авторизованным пользователям.
        """
        url_for_comments = f'/posts/{PostURLTest.post.id}/comment/'
        url_redirect_for_comments = f'/posts/{PostURLTest.post.id}/'
        urls_for_subscriptions = (
            f'/profile/{PostURLTest.author.username}/follow/',
            f'/profile/{PostURLTest.author.username}/unfollow/',
        )
        urls_redirect_for_subscriptions = ('/profile/'
                                           f'{PostURLTest.author.username}/')

        response = self.authorized_client.get(url_for_comments, follow=True)
        self.assertRedirects(
            response,
            url_redirect_for_comments,
            msg_prefix=('URL-адрес недоступен для '
                        'авторизованного пользователя')
        )
        for address in urls_for_subscriptions:
            with self.subTest(address=address):
                response = self.authorized_client.get(address, follow=True)
                self.assertRedirects(
                    response,
                    urls_redirect_for_subscriptions,
                    msg_prefix=('URL-адрес недоступен для '
                                'авторизованного пользователя')
                )

    def test_urls_accessibility_wo_redirection_for_post_authors(self):
        """Проверка URL-адресов без дефолтного редиректа,
        доступных только автору поста."""
        for address in PostURLTest.urls_for_post_authors_wo_redirection:
            with self.subTest(address=address):
                response = self.authorized_author.get(address)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK.value,
                    'URL-адрес недоступен для автора поста'
                )

    def test_urls_accessibility_w_redirection_for_post_authors(self):
        """Проверка URL-адресов с дефолтным редиректорм,
        доступных только автору поста."""
        url_profile = (f'/profile/{PostURLTest.author.username}/')
        for address in PostURLTest.urls_for_post_authors_w_redirection:
            with self.subTest(address=address):
                response = self.authorized_author.get(address)
                self.assertRedirects(
                    response,
                    url_profile,
                    msg_prefix='URL-адрес недоступен для автора поста'
                )

    def test_urls_accessibility_for_comment_authors(self):
        """Проверка URL-адресов, доступных только автору комментария."""
        url_post_detail = f'/posts/{PostURLTest.post.id}/'
        for address in self.urls_for_comment_authors:
            with self.subTest(address=address):
                response = self.authorized_author.get(address, follow=True)
                self.assertRedirects(
                    response,
                    url_post_detail,
                    msg_prefix='URL-адрес недоступен для автора комментария'
                )

    def test_urls_for_authorized_redirect_unauthorized(self):
        """Проверка редиректа неавторизованного пользователя с URL-адресов,
        доступных только авторизованным пользователям."""
        url_login_redirect = '/auth/login/?next='
        all_urls_for_authorized = (
            PostURLTest.urls_for_authorized_w_redirection
            + PostURLTest.urls_for_authorized_wo_redirection
            + PostURLTest.urls_for_post_authors_w_redirection
            + PostURLTest.urls_for_post_authors_wo_redirection
            + self.urls_for_comment_authors
        )
        for address in all_urls_for_authorized:
            with self.subTest(address=address):
                response = self.unauthorized_client.get(address, follow=True)
                self.assertRedirects(
                    response,
                    url_login_redirect + address,
                    msg_prefix=('Редирект URL-адреса для неавторизованных '
                                'пользователей не работает')
                )

    def test_urls_for_post_authors_redirect_authorized(self):
        """Проверка редиректа авторизованного пользователя с URL-адресов,
        доступных только автору поста."""
        url_post_detail = f'/posts/{PostURLTest.post.id}/'
        all_urls_for_authors = (
            PostURLTest.urls_for_post_authors_w_redirection
            + PostURLTest.urls_for_post_authors_wo_redirection
        )
        for address in all_urls_for_authors:
            with self.subTest(address=address):
                response = self.authorized_client.get(address, follow=True)
                self.assertRedirects(
                    response,
                    url_post_detail,
                    msg_prefix=('Редирект URL-адреса для авторизованных'
                                'пользователей, не являющихся авторами поста, '
                                'не работает')
                )

    def test_urls_for_comment_authors_redirect_authorized(self):
        """Проверка редиректа авторизованного пользователя с URL-адреса,
        доступного только автору комментария."""
        url_post_detail = f'/posts/{PostURLTest.post.id}/'
        for address in self.urls_for_comment_authors:
            with self.subTest(address=address):
                response = self.authorized_client.get(address, follow=True)
                self.assertRedirects(
                    response,
                    url_post_detail,
                    msg_prefix=('Редирект URL-адреса для авторизованных '
                                'пользователей, не являющихся авторами '
                                'комментария, не работает')
                )

    def test_urls_use_correct_templates(self):
        """Проверка использования URL-адресом соответствующего шаблона."""
        urls_templates = {
            '/': 'posts/index.html',
            '/create/': 'posts/create_post.html',
            '/follow/': 'posts/follow.html',
            f'/group/{PostURLTest.group.slug}/': 'posts/group_list.html',
            f'/profile/{PostURLTest.author.username}/': 'posts/profile.html',
            f'/posts/{PostURLTest.post.id}/': 'posts/post_detail.html',
            f'/posts/{PostURLTest.post.id}/edit/': 'posts/create_post.html',
        }
        for address, template in urls_templates.items():
            with self.subTest(address=address):
                response = self.authorized_author.get(address)
                self.assertTemplateUsed(
                    response,
                    template,
                    'URL-адрес использует неверный шаблон'
                )
