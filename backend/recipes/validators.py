from rest_framework.validators import ValidationError

from recipes.models import Ingredient, Tag


def validate_ingredients(data):
    """Валидация ингредиентов."""
    if not data:
        raise ValidationError({'ingredients': ['Обязательное поле.']})
    if len(data) < 1:
        raise ValidationError({'ingredients': ['Не переданы ингредиенты.']})
    unique_ingredient = []
    for ingredient in data:
        if not ingredient.get('id'):
            raise ValidationError({'ingredients': ['Отсутствует id ингредиента.']})
        id = ingredient.get('id')
        if not Ingredient.objects.filter(id=id).exists():
            raise ValidationError({'ingredients': ['Ингредиента нет в БД.']})
        if id in unique_ingredient:
            raise ValidationError(
                {'ingredients': ['Нельзя дублировать имена ингредиентов.']})
        unique_ingredient.append(id)
        amount = int(ingredient.get('amount'))
        if amount < 1:
            raise ValidationError({'amount': ['Количество не может быть менее 1.']})
    return data


def validate_tags(data):
    """Валидация тэгов."""
    if not data:
        raise ValidationError({'tags': ['Обязательное поле.']})
    if len(data) < 1:
        raise ValidationError({'tags': ['Хотя бы один тэг должен быть указан.']})
    for tag in data:
        if not Tag.objects.filter(id=tag).exists():
            raise ValidationError({'tags': ['Тэг отсутствует в БД.']})
    return data
