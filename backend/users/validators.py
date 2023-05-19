from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_me_name(username):
    if username.lower() in ['me', 'admin']:
        raise ValidationError(_(
            'Некорректное имя пользователя %(username)s'
        ), params={'username': username})
    return username