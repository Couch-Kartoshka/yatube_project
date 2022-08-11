import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Comment, Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormPostTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Test_slug',
            description='Тестовое описание',
        )
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

    def setUp(self):
        self.authorized_author = Client()
        self.authorized_author.force_login(PostFormPostTest.author)

    def tearDown(self):
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post(self):
        """Проверка создания валидной формой нового поста в БД."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст нового поста',
            'group': PostFormPostTest.group.id,
            'image': PostFormPostTest.image,
        }
        response = self.authorized_author.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', args=[PostFormPostTest.author.username]),
            msg_prefix='Редирект на страницу профайла не работает',
        )
        self.assertEqual(
            Post.objects.count(),
            posts_count + 1,
            'Количество записей в БД не увеличивается',
        )
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текст нового поста',
                group=PostFormPostTest.group,
                author=PostFormPostTest.author,
                image=f'posts/{PostFormPostTest.image.name}',
            ).exists(),
            'Новый пост не был добавлен в БД',
        )

    def test_edit_post(self):
        """Проверка изменения валидной формой существующего поста в БД."""
        post = Post.objects.create(
            text='Тестовый текст существующего поста',
            group=PostFormPostTest.group,
            author=PostFormPostTest.author,
            image=PostFormPostTest.image,
        )
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Измененный тестовый текст существующего поста',
            'group': PostFormPostTest.group.id,
        }
        response = self.authorized_author.post(
            reverse('posts:post_edit', args=[post.id]),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', args=[post.id]),
            msg_prefix='Редирект на детальную страницу поста не работает',
        )
        self.assertEqual(
            Post.objects.count(),
            posts_count,
            'Происходит увеличение записей в БД при редактировании поста',
        )
        self.assertTrue(
            Post.objects.filter(
                id=post.id,
                text='Измененный тестовый текст существующего поста',
                group=PostFormPostTest.group,
                author=PostFormPostTest.author,
                image=f'posts/{PostFormPostTest.image.name}',
            ).exists(),
        )


class PostFormCommentTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            text='Тестовый текст поста',
            author=cls.author,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostFormCommentTest.author)

    def test_add_comment(self):
        """Проверка создания валидной формой нового комментария в БД."""
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Тестовый текст нового комментария',
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', args=[PostFormCommentTest.post.id]),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', args=[PostFormCommentTest.post.id]),
            msg_prefix='Редирект на детальную страницу поста не работает',
        )
        self.assertEqual(
            Comment.objects.count(),
            comments_count + 1,
            'Количество записей в БД не увеличивается',
        )
        self.assertTrue(
            Comment.objects.filter(
                text='Тестовый текст нового комментария',
                author=PostFormCommentTest.author,
                post=PostFormCommentTest.post,
            ).exists(),
            'Новый комментарий не был добавлен в БД',
        )
