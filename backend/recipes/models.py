from django.core.validators import MinValueValidator
from django.db import models
from users.models import User


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=255,
    )
    measurement_unit = models.SlugField(
        verbose_name='Еденица измерения',
        max_length=255,
    )
    verbose_name = 'Ингредиент'
    verbose_name_plural = 'Ингредиенты'

    class Meta:
        ordering = ('id',)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название тега', max_length=255, blank=False, unique=True
    )
    color = models.CharField(
        verbose_name='Цветовой HEX-код', max_length=7, blank=False, unique=True
    )
    slug = models.SlugField(
        verbose_name='Slug', max_length=255, blank=False, unique=True
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name

    def clean(self):
        if self.name.lower() == self.color.lower():
            raise models.ValidationError(
                'Название и цвет не должны совпадать.'
            )


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='автор',
        related_name='recipes',
        db_index=True,
    )
    name = models.CharField(
        verbose_name='Название', max_length=255
    )
    image = models.ImageField(
        verbose_name='Картинка', upload_to='backend/'
    )
    description = models.TextField(
        verbose_name='Текстовое описание'
    )
    ingredients = models.ManyToManyField(
        'Ingredient',
        related_name='recipe_ingredients',
        through='IngredientAmount',
    )
    tags = models.ManyToManyField('Tag', through='TagsInRecipe')
    cooking_time = models.PositiveIntegerField(
        validators=[
            MinValueValidator(
                1, 'Время приготовления блюда не может быть меньше 1 минуты.'
            )
        ]
    )
    is_favorited = models.ManyToManyField(
        User, through='Favorite', related_name='is_favorited'
    )
    is_in_shopping_cart = models.ManyToManyField(
        User, through='CartList', related_name='cart_list'
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-id']
        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'


class IngredientAmount(models.Model):
    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        related_name='ingredients_amount',
        verbose_name='Рецепт',
        db_index=True,
    )
    ingredient = models.ForeignKey(
        'Ingredient',
        on_delete=models.PROTECT,
        related_name='ingredient_in_recipes',
        verbose_name='Ингредиент',
        db_index=True,
    )
    amount = models.PositiveIntegerField(
        validators=[MinValueValidator(1, 'Количество не может быть меньше 1')]
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredient_in_recipe',
            )
        ]


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='Пользователь',
        db_index=True,
    )
    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='Рецепт',
        db_index=True,
    )

    def __str__(self):
        return f'{self.user.username} добавил {self.recipe.name} в избраннное'

    class Meta:
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_user_recipe_favorite'
            )
        ]
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'


class TagsInRecipe(models.Model):
    recipe = models.ForeignKey(
        'Recipe', on_delete=models.CASCADE, related_name='tags_in_recipe'
    )
    tag = models.ForeignKey(
        'Tag', on_delete=models.CASCADE, related_name='tags_in_recipe'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'tag'], name='unique_tag_per_recipe'
            )
        ]
        verbose_name = 'Тег в рецепте'
        verbose_name_plural = 'Теги в рецептах'


class CartList(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'], name='unique_shopping_list_recipe'
            )
        ]
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
