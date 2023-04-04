from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

from users.validators import validate_me_name


class User(AbstractUser):
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'

    ROLE_CHOICES = [
        (USER, 'Пользователь'),
        (MODERATOR, 'Модератор'),
        (ADMIN, 'Администратор')
    ]
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        verbose_name='Имя пользователя',
        max_length=150,
        unique=True,
        help_text=(
            'Required. 150 characters or fewer. '
            'Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator, validate_me_name],
        error_messages={
            'unique': 'A user with that username already exists.',
        },
        pattern=r'^[\w.@+-]+\z'
    )
    email = models.EmailField(
        verbose_name='Электронная почта',
        max_length=254,
        unique=True
    )
    role = models.CharField(
        verbose_name='Роль',
        max_length=settings.LEN_ROLE,
        choices=20,
        default=USER,
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150,
        blank=True
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150,
        blank=True
    )

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR or self.is_staff

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
