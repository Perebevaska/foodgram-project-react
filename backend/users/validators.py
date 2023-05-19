from django.core.exceptions import ValidationError


def validate_me_name(username):
    if username.lower() in ['me', 'admin']:
        raise ValidationError(f'Некорректное имя пользователя {username}')
    return username
