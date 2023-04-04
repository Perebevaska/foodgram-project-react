from django.core.exceptions import ValidationError


def validate_me_name(username):
    if username.lower() == 'me':
        raise ValidationError(f'Некорректное имя пользователя {username}')
    return username
