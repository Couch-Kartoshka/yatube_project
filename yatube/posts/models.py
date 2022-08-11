from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        verbose_name='Группа',
        max_length=200,
        help_text='Группа, в которую будут добавляться посты'
    )
    slug = models.SlugField(
        verbose_name='Идентификатор',
        unique=True,
        null=False,
        help_text='Уникальный идентификатор группы для URL'
    )
    description = models.TextField(
        verbose_name='Описание',
        help_text='Описание предназначения группы'
    )

    class Meta:
        verbose_name = 'Группа постов'
        verbose_name_plural = 'Группы постов'

    def __str__(self) -> str:
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст поста',
        help_text='Текст нового поста'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата создания поста',
        auto_now_add=True,
        db_index=True,
        help_text='Дата сохраняется автоматически'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор поста',
        help_text='Автор сохраняется автоматически'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа',
        blank=True,
        null=True,
        help_text='Группа, к которой будет относиться пост'
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='posts/',
        blank=True,
        help_text='Заглавная картинка к посту'
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self) -> str:
        return self.text[:30]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост комментария',
        help_text='Пост, к которому принадлежит комментарий'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария',
        help_text='Автор сохраняется автоматически'
    )
    text = models.TextField(
        verbose_name='Текст комментария',
        help_text='Текст нового комментария к посту'
    )
    created = models.DateTimeField(
        verbose_name='Дата создания комментария',
        auto_now_add=True,
        db_index=True,
        help_text='Дата сохраняется автоматически'
    )

    class Meta:
        ordering = ('created',)
        verbose_name = 'Комментарий поста'
        verbose_name_plural = 'Комментарии постов'

    def __str__(self) -> str:
        return self.text[:30]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
        help_text='Пользователь, подписанный на определенных авторов'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор постов',
        help_text='Автор, на которого подписаны пользователи'
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_subscription'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='prevent_self_subscription'
            )
        )
        verbose_name = 'Подписка на автора'
        verbose_name_plural = 'Подписки на авторов'

    def __str__(self) -> str:
        return (f'Пользователь {self.user.username} подписан'
                f'на автора {self.author.username}')
