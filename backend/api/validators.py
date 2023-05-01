from recipes.models import Tag, Ingredient
from rest_framework import serializers


def validate_tags(self, tags):
    if not tags:
        raise serializers.ValidationError('Обязательное поле "tags".')
    tag_ids = set(tags)
    missing_tags = Tag.objects.filter(id__in=tag_ids).values_list('id', flat=True)
    if len(missing_tags) < len(tag_ids):
        invalid_tags = tag_ids - set(missing_tags)
        raise serializers.ValidationError(f'Теги {invalid_tags} не найдены.')
    return tags

def validate_ingredients(self, data):
    ingredients = data.get('ingredients')
    if not ingredients:
        raise serializers.ValidationError('Обязательное поле "ingredients".')
    if len(ingredients) < 1:
        raise serializers.ValidationError('Не переданы ингредиенты.')
    unique_ingredient_ids = set()
    for ingredient in ingredients:
        ingredient_id = ingredient.get('id')
        if not ingredient_id:
            raise serializers.ValidationError('Отсутствует id ингредиента.')
        if ingredient_id in unique_ingredient_ids:
            raise serializers.ValidationError('Нельзя дублировать имена ингредиентов.')
        unique_ingredient_ids.add(ingredient_id)
    ingredient_ids = [ingredient.get('id') for ingredient in ingredients]
    if not Ingredient.objects.filter(id__in=ingredient_ids).count() == len(ingredient_ids):
        raise serializers.ValidationError('Ингредиенты не найдены.')
    for ingredient in ingredients:
        amount = ingredient.get('amount')
        if not isinstance(amount, int) or amount < 1:
            raise serializers.ValidationError('Количество должно быть целым числом больше 0.')
    return data