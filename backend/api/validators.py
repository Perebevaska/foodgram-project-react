from recipes.models import Ingredient, Tag
from rest_framework import serializers


def validate_tags(self, tags):
    if not tags:
        raise serializers.ValidationError('Обязательное поле "tags".')
    tag_ids = set(tags)
    if len(tag_ids) != len(tags):
        raise serializers.ValidationError('Нельзя дублировать теги.')
    missing_tags = Tag.objects.filter(id__in=tag_ids).values_list('id', flat=True)
    if len(missing_tags) < len(tag_ids):
        invalid_tags = tag_ids - set(missing_tags)
        raise serializers.ValidationError(f'Теги {invalid_tags} не найдены.')
    return list(tag_ids)

def validate_ingredients(self, data):
    ingredients = data.get('ingredients')
    if not ingredients:
        raise serializers.ValidationError('Обязательное поле "ingredients".')
    unique_ingredient_ids = set(ingredient['id'] for ingredient in ingredients)
    if len(unique_ingredient_ids) != len(ingredients):
        raise serializers.ValidationError('Нельзя дублировать ингредиенты.')
    ingredient_ids = Ingredient.objects.filter(id__in=unique_ingredient_ids).values_list('id', flat=True)
    if len(ingredient_ids) != len(unique_ingredient_ids):
        raise serializers.ValidationError('Некоторые ингредиенты не найдены.')
    return data