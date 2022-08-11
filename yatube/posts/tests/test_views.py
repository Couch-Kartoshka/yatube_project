import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Comment, Follow, Group, Post

from yatube.settings import POSTS_PER_PAGE

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth')
        cls.image = SimpleUploadedFile(
            name='test_image.jpeg',
            content=(
                b'\x47\x49\x46\x38\x39\x61\x02\x00'
                b'\x01\x00\x80\x00\x00\x00\x00\x00'
                b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                b'\x0A\x00\x3B'
            ),
            content_type='image/jpeg',
        )
        cls.first_group = Group.objects.create(
            title='Тестовая группа 1',
            slug='Test_slug1',
            description='Тестовое описание группы 1',
        )
        cls.post_from_first_group = Post.objects.create(
            text='Тестовый текст поста из группы 1',
            author=cls.author,
            group=cls.first_group,
            image=cls.image,
        )
        cls.second_group = Group.objects.create(
            title='Тестовая группа 2',
            slug='Test_slug2',
            description='Тестовое описание группы 2',
        )
        cls.post_from_second_group = Post.objects.create(
            text='Тестовый текст поста из группы 2',
            author=cls.author,
            group=cls.second_group,
            image=cls.image,
        )
        cls.post_without_group = Post.objects.create(
            text='Тестовый текст поста без группы',
            author=cls.author,
            image=cls.image,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.user = User.objects.create_user(username='Test user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.authorized_author = Client()
        self.authorized_author.force_login(PostViewTest.author)

        cache.clear()

    def test_pages_use_correct_templates(self):
        """Проверка использования страницами соответствующего шаблона."""
        author = PostViewTest.author
        post = PostViewTest.post_from_first_group
        group = PostViewTest.first_group
        page_templates = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:follow_index'): 'posts/follow.html',
            reverse('posts:group_list', args=[group.slug]):
                   ('posts/group_list.html'),
            reverse('posts:profile', args=[author.username]):
                   ('posts/profile.html'),
            reverse('posts:post_detail', args=[post.id]):
                   ('posts/post_detail.html'),
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit', args=[post.id]):
                   ('posts/create_post.html'),
        }
        for reverse_name, template in page_templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_author.get(reverse_name)
                self.assertTemplateUsed(
                    response,
                    template,
                    'Страница использует неверный шаблон'
                )

    def test_pages_use_correct_context_page_title(self):
        """Проверка использования страницами соответствующего заголовка."""
        author = PostViewTest.author
        post = PostViewTest.post_from_first_group
        group = PostViewTest.first_group
        page_titles = {
            reverse('posts:index'): 'Последние обновления на сайте',
            reverse('posts:follow_index'):
                   ('Последние обновления у избранных авторов'),
            reverse('posts:group_list', args=[group.slug]):
                   (f'Записи сообщества {group.title}'),
            reverse('posts:profile', args=[author.username]):
                   (f'Профайл пользователя @{author.username}'),
            reverse('posts:post_detail', args=[post.id]):
                   (f'Пост {str(post)}'),
            reverse('posts:post_create'): 'Новый пост',
            reverse('posts:post_edit', args=[post.id]):
                   ('Редактировать пост'),
        }
        for reverse_name, expected_page_title in page_titles.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_author.get(reverse_name)
                current_page_title = response.context['page_title']
                self.assertEqual(
                    current_page_title,
                    expected_page_title,
                    'Страница использует неверный заголовок'
                )

    def test_index_page_uses_correct_context(self):
        """Проверка передачи главной странице корректного контекста."""
        posts = [
            PostViewTest.post_from_first_group,
            PostViewTest.post_from_second_group,
            PostViewTest.post_without_group,
        ]
        response = self.authorized_client.get(reverse('posts:index'))
        page_objects = response.context['page_obj']
        for post in posts:
            with self.subTest(post=post):
                self.assertIn(
                    post,
                    page_objects,
                    'Пост не передан в контекст главной страницы',
                )

    def test_follow_index_page_uses_correct_context(self):
        """Проверка передачи странице ленты подписок корректного контекста."""
        author_follower = self.user
        not_author_follower = User.objects.create_user(username='Test user 2')
        second_authorized_client = Client()
        second_authorized_client.force_login(not_author_follower)
        Follow.objects.create(
            user=author_follower,
            author=PostViewTest.author,
        )
        posts = [
            PostViewTest.post_from_first_group,
            PostViewTest.post_from_second_group,
            PostViewTest.post_without_group,
        ]

        response = self.authorized_client.get(reverse('posts:follow_index'))
        page_objects = response.context['page_obj']
        for post in posts:
            with self.subTest(post=post):
                self.assertIn(
                    post,
                    page_objects,
                    'Пост не передан в контекст страницы для подписчика',
                )
        response = second_authorized_client.get(reverse('posts:follow_index'))
        page_objects = response.context['page_obj']
        for post in posts:
            with self.subTest(post=post):
                self.assertNotIn(
                    post,
                    page_objects,
                    'Пост ошибочно передан в контекст страницы не подписчику',
                )

    def test_group_page_posts_uses_correct_context(self):
        """Проверка передачи странице с постами группы
        корректного контекста."""
        first_group = PostViewTest.first_group
        post_from_first_group = PostViewTest.post_from_first_group
        post_from_second_group = PostViewTest.post_from_second_group
        response = self.authorized_client.get(
            reverse('posts:group_list', args=[first_group.slug])
        )
        page_objects = response.context['page_obj']
        self.assertIn(
            post_from_first_group,
            page_objects,
            'Пост не передан в контекст страницы о группе'
        )
        self.assertNotIn(
            post_from_second_group,
            page_objects,
            'Пост неверно передан в контекст страницы о чужой группе'
        )
        self.assertEqual(
            first_group,
            response.context.get('group'),
            'Группа не передана в контекст страницы о группе'
        )

    def test_profile_page_uses_correct_context(self):
        """Проверка передачи странице профайла пользователя
        корректного контекста."""
        author = PostViewTest.author
        posts = [
            PostViewTest.post_from_first_group,
            PostViewTest.post_from_second_group,
            PostViewTest.post_without_group,
        ]
        Follow.objects.create(
            user=self.user,
            author=PostViewTest.author,
        )
        response = self.authorized_client.get(
            reverse('posts:profile', args=[author.username])
        )
        page_objects = response.context['page_obj']
        for post in posts:
            with self.subTest(post=post):
                self.assertIn(
                    post,
                    page_objects,
                    'Пост не передан в контекст страницы о пользователе',
                )
        self.assertEqual(
            author,
            response.context.get('author'),
            'Страница не содержит данные о пользователе'
        )
        self.assertEqual(
            True,
            response.context.get('following'),
            'Страница не содержит данные о подписке на пользователя'
        )

    def test_follow_page_works_correctly(self):
        """Проверка работоспособности системы подписок на авторов."""
        self.authorized_client.get(
            reverse('posts:profile_follow',
                    args=[PostViewTest.author.username])
        )
        self.assertTrue(
            Follow.objects.filter(
                user=self.user,
                author=PostViewTest.author,
            ).exists(),
            'Подписка на автора не была добавлена в БД',
        )

        subscriptions_count = Follow.objects.count()
        self.authorized_client.get(
            reverse('posts:profile_follow',
                    args=[PostViewTest.author.username])
        )
        self.assertEqual(
            subscriptions_count,
            Follow.objects.count(),
            'Пользователь может повторно подписываться на одного автора'
        )

        self.authorized_client.get(
            reverse('posts:profile_follow',
                    args=[self.user.username])
        )
        self.assertFalse(
            Follow.objects.filter(
                user=self.user,
                author=self.user,
            ).exists(),
            'Пользователь может ошибочно подписываться на самого себя',
        )

    def test_unfollow_page_works_correctly(self):
        """Проверка работоспособности системы отписок от авторов."""
        Follow.objects.create(
            user=self.user,
            author=PostViewTest.author,
        )
        self.authorized_client.get(
            reverse('posts:profile_unfollow',
                    args=[PostViewTest.author.username])
        )
        self.assertFalse(
            Follow.objects.filter(
                user=self.user,
                author=PostViewTest.author,
            ).exists(),
            'Подписка на автора не была удалена из БД',
        )

    def test_detail_page_uses_correct_context(self):
        """Проверка передачи странице просмотра поста корректного контекста."""
        post = PostViewTest.post_from_first_group
        comment = Comment.objects.create(
            text='Тестовый текст нового комментария',
            author=self.user,
            post=post,
        )
        comment_form_fields = {
            'text': forms.fields.CharField,
        }
        response = self.authorized_client.get(
            reverse('posts:post_detail', args=[post.id])
        )
        self.assertEqual(
            post,
            response.context.get('post'),
            'Страница не содержит данные о посте'
        )
        self.assertIn(
            comment,
            response.context.get('comments'),
            'Страница не содержит данные о комментарии к посту'
        )
        for value, expected_field in comment_form_fields.items():
            with self.subTest(value=value):
                form_all_fields = response.context.get('form').fields
                current_field = form_all_fields.get(value)
                self.assertIsInstance(
                    current_field,
                    expected_field,
                    'Тип поля формы не соответствует ожидаемому'
                )

    def test_create_edit_pages_use_correct_context(self):
        """Проверка передачи страницам создания и редактирования поста
        корректного контекста."""
        post = PostViewTest.post_from_first_group
        pages_with_post_form = [
            reverse('posts:post_create'),
            reverse('posts:post_edit', args=[post.id]),
        ]
        post_form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for reverse_name in pages_with_post_form:
            for value, expected_field in post_form_fields.items():
                with self.subTest(value=value):
                    response = self.authorized_author.get(reverse_name)
                    form_all_fields = response.context.get('form').fields
                    current_field = form_all_fields.get(value)
                    self.assertIsInstance(
                        current_field,
                        expected_field,
                        'Тип поля формы не соответствует ожидаемому'
                    )

    def test_post_delete_page_works_correctly(self):
        """Проверка работоспособности системы удаления постов."""
        post = Post.objects.create(
            text='Тестовый текст поста',
            author=PostViewTest.author,
        )
        self.authorized_client.get(
            reverse('posts:post_delete', args=[post.id])
        )
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текст поста',
                author=PostViewTest.author,
            ).exists(),
            'Пост был ошибочно удален чужим автором из БД',
        )
        self.authorized_author.get(
            reverse('posts:post_delete', args=[post.id])
        )
        self.assertFalse(
            Post.objects.filter(
                text='Тестовый текст поста',
                author=PostViewTest.author,
            ).exists(),
            'Пост не был удален его автором из БД',
        )

    def test_comment_delete_page_works_correctly(self):
        """Проверка работоспособности системы удаления комментариев."""
        post = PostViewTest.post_from_first_group
        comment = Comment.objects.create(
            text='Тестовый текст комментария к посту',
            author=self.user,
            post=post,
        )
        self.authorized_author.get(
            reverse('posts:comment_delete', args=[comment.id])
        )
        self.assertTrue(
            Comment.objects.filter(
                text='Тестовый текст комментария к посту',
                author=self.user,
                post=post,
            ).exists(),
            'Комментарий был ошибочно удален чужим автором из БД',
        )
        self.authorized_client.get(
            reverse('posts:comment_delete', args=[comment.id])
        )
        self.assertFalse(
            Comment.objects.filter(
                text='Тестовый текст комментария к посту',
                author=self.user,
                post=post,
            ).exists(),
            'Комментарий не был удален его автором из БД',
        )


class PaginatorPostViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Test_slug',
            description='Тестовое описание',
        )
        cls.post_texts = [
            f'Текст поста {number}' for number in range(0, 11)
        ]
        cls.posts = [
            Post.objects.create(
                text=post_text,
                author=cls.author,
                group=cls.group
            ) for post_text in cls.post_texts
        ]

    def setUp(self):
        self.user = User.objects.create_user(username='Test user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        cache.clear()

    def test_page_paginator_works_correctly(self):
        """Проверка корректной работы пажинатора страниц."""
        Follow.objects.create(
            user=self.user,
            author=PaginatorPostViewTest.author,
        )
        pages_with_paginator = [
            reverse('posts:index'),
            reverse('posts:follow_index'),
            reverse('posts:group_list',
                    args=[PaginatorPostViewTest.group.slug]),
            reverse('posts:profile',
                    args=[PaginatorPostViewTest.author.username]),
        ]
        posts_on_last_page = Post.objects.count() % POSTS_PER_PAGE
        for reverse_name in pages_with_paginator:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(
                    len(response.context['page_obj']),
                    POSTS_PER_PAGE,
                    'Неверное кол-во постов на первой странице пажинатора'
                )
                response = self.authorized_client.get(reverse_name + '?page=2')
                self.assertEqual(
                    len(response.context['page_obj']),
                    posts_on_last_page,
                    'Неверное кол-во постов на последней странице пажинатора'
                )


class CachePostViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Test_slug',
            description='Тестовое описание',
        )

    def setUp(self):
        self.user = User.objects.create_user(username='Test user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        cache.clear()

    def test_index_page_cache_works_correctly(self):
        """Проверка корректной работы кеширования главной страницы."""
        index_page = reverse('posts:index')
        post = Post.objects.create(
            text='Тестовый текст поста',
            author=CachePostViewTest.author,
            group=CachePostViewTest.group,
        )

        response = self.authorized_client.get(index_page)
        saved_content = response.content
        post.delete()
        response = self.authorized_client.get(index_page)
        cached_content = response.content
        self.assertEqual(
            saved_content,
            cached_content,
            'Кеширование главной страницы не работает'
        )

        cache.clear()
        response = self.authorized_client.get(index_page)
        cleared_content = response.content
        self.assertNotEqual(
            cached_content,
            cleared_content,
            'Очистка кеша не удаляет кешированный пост'
        )

    def test_follow_page_cache_works_correctly(self):
        """Проверка корректной работы кеширования страницы ленты подписок."""
        follow_index_page = reverse('posts:follow_index')
        post = Post.objects.create(
            text='Тестовый текст поста',
            author=CachePostViewTest.author,
            group=CachePostViewTest.group,
        )
        Follow.objects.create(
            user=self.user,
            author=CachePostViewTest.author,
        )

        response = self.authorized_client.get(follow_index_page)
        saved_content = response.content
        post.delete()
        response = self.authorized_client.get(follow_index_page)
        cached_content = response.content
        self.assertEqual(
            saved_content,
            cached_content,
            'Кеширование страницы ленты подписок не работает'
        )

        cache.clear()
        response = self.authorized_client.get(follow_index_page)
        cleared_content = response.content
        self.assertNotEqual(
            saved_content,
            cleared_content,
            'Очистка кеша не удаляет кешированный пост'
        )
