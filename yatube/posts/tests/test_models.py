from django.contrib.auth import get_user_model
from django.test import TestCase
from posts.models import Comment, Follow, Group, Post

User = get_user_model()


class PostModelPostTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            text='Тестовый текст поста, состоящий из более 30 символов',
            author=cls.author,
        )

    def test_post_model_has_correct_string_output(self):
        """Проверка корректности работы метода __str__ у модели поста."""
        self.assertEqual(
            str(PostModelPostTest.post),
            PostModelPostTest.post.text[:30],
            'Метод __str__ работает неправильно'
        )

    def test_post_verbose_names(self):
        """Проверка совпадения verbose_name полей модели поста
        с ожидаемым значением."""
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата создания поста',
            'author': 'Автор поста',
            'group': 'Группа',
        }
        for field, expect_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    PostModelPostTest.post._meta.get_field(field).verbose_name,
                    expect_value,
                    'verbose_name не совпадает с ожидаемым'
                )

    def test_post_help_texts(self):
        """Проверка совпадения help_text полей модели поста
        с ожидаемым значением."""
        field_help_texts = {
            'text': 'Текст нового поста',
            'pub_date': 'Дата сохраняется автоматически',
            'author': 'Автор сохраняется автоматически',
            'group': 'Группа, к которой будет относиться пост',
        }
        for field, expect_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    PostModelPostTest.post._meta.get_field(field).help_text,
                    expect_value,
                    'help_text не совпадает с ожидаемым'
                )


class PostModelGroupTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )

    def test_group_model_has_correct_string_output(self):
        """Проверка корректности работы метода __str__ у модели группы."""
        self.assertEqual(
            str(PostModelGroupTest.group),
            PostModelGroupTest.group.title,
            'Метод __str__ работает неправильно'
        )

    def test_group_verbose_names(self):
        """Проверка совпадения verbose_name полей модели группы
        с ожидаемым значением."""
        field_verboses = {
            'title': 'Группа',
            'slug': 'Идентификатор',
            'description': 'Описание',
        }
        for field, expect_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    PostModelGroupTest.group._meta.get_field(
                        field
                    ).verbose_name,
                    expect_value,
                    'verbose_name не совпадает с ожидаемым'
                )

    def test_group_help_texts(self):
        """Проверка совпадения help_text полей модели группы
        с ожидаемым значением."""
        field_help_texts = {
            'title': 'Группа, в которую будут добавляться посты',
            'slug': 'Уникальный идентификатор группы для URL',
            'description': 'Описание предназначения группы',
        }
        for field, expect_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    PostModelGroupTest.group._meta.get_field(field).help_text,
                    expect_value,
                    'help_text не совпадает с ожидаемым'
                )


class PostModelCommentTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            text='Тестовый текст поста',
            author=cls.author,
        )
        cls.comment = Comment.objects.create(
            text='Тестовый текст комментария, состоящий из более 30 символов',
            author=cls.author,
            post=cls.post,
        )

    def test_comment_model_has_correct_string_output(self):
        """Проверка корректности работы метода __str__ у модели комментария."""
        self.assertEqual(
            str(PostModelCommentTest.comment),
            PostModelCommentTest.comment.text[:30],
            'Метод __str__ работает неправильно'
        )

    def test_comment_verbose_names(self):
        """Проверка совпадения verbose_name полей модели комментария
        с ожидаемым значением."""
        field_verboses = {
            'post': 'Пост комментария',
            'author': 'Автор комментария',
            'text': 'Текст комментария',
            'created': 'Дата создания комментария',
        }
        for field, expect_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    (PostModelCommentTest.comment.
                     _meta.get_field(field).verbose_name),
                    expect_value,
                    'verbose_name не совпадает с ожидаемым'
                )

    def test_comment_help_texts(self):
        """Проверка совпадения help_text полей модели комментария
        с ожидаемым значением."""
        field_help_texts = {
            'post': 'Пост, к которому принадлежит комментарий',
            'author': 'Автор сохраняется автоматически',
            'text': 'Текст нового комментария к посту',
            'created': 'Дата сохраняется автоматически',
        }
        for field, expect_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    (PostModelCommentTest.comment.
                     _meta.get_field(field).help_text),
                    expect_value,
                    'help_text не совпадает с ожидаемым'
                )


class PostModelFollowTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth')
        cls.user = User.objects.create_user(username='user')
        cls.subscription = Follow.objects.create(
            user=cls.user,
            author=cls.author,
        )

    def test_follow_model_has_correct_string_output(self):
        """Проверка корректности работы метода __str__ у модели подписок."""
        self.assertEqual(
            str(PostModelFollowTest.subscription),
            (f'Пользователь {PostModelFollowTest.user.username} подписан'
             f'на автора {PostModelFollowTest.author.username}'),
            'Метод __str__ работает неправильно'
        )

    def test_follow_verbose_names(self):
        """Проверка совпадения verbose_name полей модели подписок
        с ожидаемым значением."""
        field_verboses = {
            'user': 'Подписчик',
            'author': 'Автор постов',
        }
        for field, expect_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    (PostModelFollowTest.subscription.
                     _meta.get_field(field).verbose_name),
                    expect_value,
                    'verbose_name не совпадает с ожидаемым'
                )

    def test_follow_help_texts(self):
        """Проверка совпадения help_text полей модели подписок
        с ожидаемым значением."""
        field_help_texts = {
            'user': 'Пользователь, подписанный на определенных авторов',
            'author': 'Автор, на которого подписаны пользователи',
        }
        for field, expect_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    (PostModelFollowTest.subscription.
                     _meta.get_field(field).help_text),
                    expect_value,
                    'help_text не совпадает с ожидаемым'
                )
