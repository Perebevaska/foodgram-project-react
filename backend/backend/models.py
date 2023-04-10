from django.db import models
from users.models import User

class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='автор'
    )
    name = models.SlugField(
        verbose_name='Название',
        max_length=255,
        unique=True,
        blank=False
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='backend/',
        blank=False
    )
    description = models.TextField(
        verbose_name='Текстовое описание',
        blank=True,
        null=True
    )

class Ingridient(models.Model):
    name = models.SlugField(
        verbose_name='Название',
        max_length=255,
        unique=True,
        blank=False
    )
    quantity = models.IntegerField(
        verbose_name='Количество',
        max_length=4,
        blank=False
    )
    measure_unit = models.SlugField(
        verbose_name='Еденица измерения',
        max_length=255,
        blank=False
    )

class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=255,
        blank=False,
        unique=True
    )
    color = models.CharField(
        verbose_name='Цветовой HEX-код',
        max_length=7,
        blank=False,
        unique=True
    )
    slug = models.SlugField(
        verbose_name='Slug',
        max_length=255,
        blank=False,
        unique=True
    )

    class Meta:
        constraints = [
            models.CheckConstraint(check=~models.Q(name=models.F('color')), name='name_color_not_equal')
        ]

    def __str__(self):
        return self.name
