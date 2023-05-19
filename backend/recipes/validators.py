from rest_framework.validators import ValidationError

from recipes.models import Ingredient, Tag


def validate_ingredients(data):
    """Валидация ингредиентов и количества."""
    if not data:
        raise ValidationError({'ingredients': [
            'Обязательное поле.']})
    if len(data) < 1:
        raise ValidationError({'ingredients': [
            'Не переданы ингредиенты.']})
    unique_ingredients = set()
    for ingredient in data:
        ingredient_id = ingredient.get('id')
        if not ingredient_id:
            raise ValidationError({'ingredients': [
                'Отсутствует id ингредиента.']})
        if not Ingredient.objects.filter(id=ingredient_id).exists():
            raise ValidationError({'ingredients': [
                'Ингредиента нет в БД.']})
        if ingredient_id in unique_ingredients:
            raise ValidationError({'ingredients': [
                'Нельзя дублировать имена ингредиентов.']})
        unique_ingredients.add(ingredient_id)
        amount = int(ingredient.get('amount', 0))
        if amount < 1:
            raise ValidationError({'amount': [
                'Количество не может быть менее 1.']})
    return data


def validate_tags(data):
    """Валидация тэгов: отсутствие
    в request, отсутствие в БД."""
    if not data:
        raise ValidationError({'tags': [
            'Обязательное поле.']})
    if len(data) < 1:
        raise ValidationError({'tags': [
            'Хотя бы один тэг должен быть указан.']})
    tag_ids = [tag.get('id') for tag in data]
    if not Tag.objects.filter(id__in=tag_ids).count() == len(tag_ids):
        raise ValidationError({'tags': [
            'Один или несколько тэгов отсутствуют в БД.']})
    return data
