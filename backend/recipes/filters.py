from django.contrib.auth.decorators import login_required
from django_filters import ModelMultipleChoiceFilter
from django_filters.rest_framework import FilterSet, filters
from rest_framework import filters
from users.models import User

from .models import Recipe, Tag


@login_required
class RecipeFilter(FilterSet):
    tags = ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    author = filters.ModelChoiceFilter(
        queryset=User.objects.all(),
        conjoined=True,
        label=('Автор'),
        help_text=('Фильтр по автору рецепта'),
    )
    is_favorited = filters.BooleanFilter(method='filter_favorited')
    is_in_shopping_cart = filters.BooleanFilter(method='filter_shopping_cart')

    def filter_tags(self, queryset, name, value):
        tags = Tag.objects.filter(slug__in=value)
        if tags.exists():
            return queryset.filter(tags__in=tags)
        return queryset.none()

    def filter_favorited(self, queryset, name, value):
        if value:
            return queryset.filter(favorite__user=self.request.user)
        return queryset

    def filter_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(sh_cart__user=self.request.user)
        return queryset

    class Meta:
        model = Recipe
        fields = ('tags', 'author')


class NameFilter(filters.SearchFilter):
    search_param = 'name'
