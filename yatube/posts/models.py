from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


TEXT_IN_FIELD = 15


class Group(models.Model):
    title = models.CharField('Заголовочек', max_length=200)
    slug = models.SlugField('Слаг адрес', unique=True)
    description = models.TextField('Описание группы')

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField('Мысли великих')
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор поста'
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Могучие группы'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.text[:TEXT_IN_FIELD]
