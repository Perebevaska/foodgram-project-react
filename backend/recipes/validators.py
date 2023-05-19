from rest_framework.validators import ValidationError

from recipes.models import Ingredient, Tag


def validate_tags(data):
    """Валидация тэгов."""
    if not data:
        raise ValidationError({'tags': ['Обязательное поле.']})
    if len(data) < 1:
        raise ValidationError({'tags': ['Минимум 1 тэг.']})
    for tag in data:
        if not Tag.objects.filter(id=tag).exists():
            raise ValidationError({'tags': ['Тэг отсутствует']})
    return data

def validate_ingredients(data):
    """Валидация ингредиентов."""
    if not data:
        raise ValidationError({'ingredients': ['Обязательное поле.']})
    if len(data) < 1:
        raise ValidationError({'ingredients': ['Не переданы ингредиенты.']})
    unique_ingredient = []
    for ingredient in data:
        id = ingredient.get('id')
        if id in unique_ingredient:
            raise ValidationError(
                {'ingredients': ['Нельзя дублировать названия ингредиентов.']})
        unique_ingredient.append(id)
        amount = int(ingredient.get('amount'))
        if amount < 1:
            raise ValidationError({'amount': [
                'Количество не может быть меньше 1.'
            ]})
    return data
