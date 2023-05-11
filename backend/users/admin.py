from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from recipes.models import (Favorite, Ingredient, IngredientAmount, Recipe,
                            CartList, Tag)
from users.models import Subscription, User


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'author')
    search_fields = ('user__username', 'author__username')


class CustomUserAdmin(UserAdmin):
    search_fields = ('email', 'username')
    list_filter = ('email', 'username')
    ordering = ('pk',)


class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color', 'slug',)
    list_editable = ('name', 'color', 'slug')
    search_fields = ('name',)
    empty_value_display = 'пусто'


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit',)
    list_editable = ('name', 'measurement_unit')
    search_fields = ('name',)
    empty_value_display = 'пусто'


class IngredientAmountInline(admin.TabularInline):
    model = IngredientAmount


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'author', 'image', 'count')
    exclude = ('ingredients',)
    inlines = (IngredientAmountInline,)
    list_filter = ('author', 'name', 'tags')
    search_fields = ('author__username', 'name', 'tags__name')
    empty_value_display = 'пусто'

    def count(self, obj):
        return obj.favorite.count()


class IngredientAmountAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'ingredient', 'amount')
    search_fields = ('recipe__name', 'ingredient__name')


class FavoriteShoppingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user__username', 'recipe__name')


admin.site.register(User, CustomUserAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(IngredientAmount, IngredientAmountAdmin)
admin.site.register(Favorite, FavoriteShoppingAdmin)
admin.site.register(CartList, FavoriteShoppingAdmin)
