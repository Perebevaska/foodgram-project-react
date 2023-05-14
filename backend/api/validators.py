from recipes.models import Ingredient, Tag
from rest_framework.validators import ValidationError


def validate_tags(tags):
    if not tags:
        raise ValidationError({'tags': ['Обязательное поле.']})
    if len(tags) < 1:
        raise ValidationError({'tags': ['Минимум 1 тег.']})
    for tag in tags:
        if not Tag.objects.filter(id=tag).exists():
            raise ValidationError({'tags': ['Тег отсутствует в базе данных.']})
    return tags


def validate_ingredients(ingredients):
    if not ingredients:
        raise ValidationError(
            {'ingredients': ['Обязательное поле.']}
        )
    if len(ingredients) < 1:
        raise ValidationError(
            {'ingredients': ['Не указаны ингредиенты.']}
        )
    unique_ingredient = []
    for ingredient in ingredients:
        if not ingredient.get('id'):
            raise ValidationError(
                {'ingredients': ['Отсутствует id ингредиента.']}
            )
        id = ingredient.get('id')
        if not Ingredient.objects.filter(id=id).exists():
            raise ValidationError(
                {'ingredients': ['Ингредиента нет в базе данных.']}
            )
        if id in unique_ingredient:
            raise ValidationError(
                {'ingredients': ['Нельзя дублировать имена ингредиентов.']}
            )
        unique_ingredient.append(id)
        amount = int(ingredient.get('amount'))
        if amount < 1:
            raise ValidationError(
                {'amount': ['Количество не может быть менее 1.']}
            )
    return ingredients
