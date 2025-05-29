from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import models

User = get_user_model()


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(
            is_published=True,
            pub_date__lte=timezone.now()
        )


class Category(models.Model):
    title = models.CharField(max_length=256, verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание')
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор',
        help_text='Идентификатор страницы для URL; разрешены символы латиницы,'
        ' цифры, дефис и подчёркивание.')
    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.')
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено')

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Location(models.Model):
    name = models.CharField(max_length=256, verbose_name='Название места')
    is_published = models.BooleanField(
        default=True, verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.')
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено')

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField(max_length=256, verbose_name='Заголовок')
    text = models.TextField(verbose_name='Текст')
    image = models.ImageField('Фото', upload_to='images', blank=True)
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text='Если установить дату и время в будущем'
        ' — можно делать отложенные публикации.')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации')
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Местоположение')
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория')
    is_published = models.BooleanField(
        default=True, verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.')
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено')
    objects = models.Manager()  # стандартный менеджер
    published = PublishedManager()  # менеджер для базовой фильтрации

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ['-pub_date']

    @property
    def comment_count(self):
        return self.comment.count()

    def __str__(self):
        return self.title


class Comment(models.Model):
    text = models.TextField('Комменатрий')
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comment',
        verbose_name='Пост',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата и время публикации',
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Автор',
    )

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('-created_at',)
