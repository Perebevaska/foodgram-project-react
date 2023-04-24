from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from users.models import User

class Ingredient(models.Model):
    name = models.SlugField(
        verbose_name='Название',
        max_length=255,
        unique=True,
        blank=False
    )
    quantity = models.IntegerField(
        verbose_name='Количество',
        blank=False,
    )
    measure_unit = models.SlugField(
        verbose_name='Еденица измерения',
        max_length=255,
        blank=False
    )
    def __str__(self):
        return self.name

    def clean(self):
        if not self.name:
            raise ValidationError('Название ингредиента обязательно.')
        if self.quantity <= 0:
            raise ValidationError('Количество должно быть больше нуля.')
        if not self.measure_unit:
            raise ValidationError('Единица измерения обязательна.')




class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=255,
        blank=False,
        unique=True
    )
    color = models.CharField(
        verbose_name='Цветовой HEX-код',
        max_length=7,
        blank=False,
        unique=True
    )
    slug = models.SlugField(
        verbose_name='Slug',
        max_length=255,
        blank=False,
        unique=True
    )

    def __str__(self):
        return self.name

    def clean(self):
        if self.name.lower() == self.color.lower():
            raise models.ValidationError('Название и цвет не должны совпадать.')

class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='автор',
        related_name='recipes',
        db_index=True
    )
    name = models.SlugField(
        verbose_name='Название',
        max_length=255,
        unique=True,
        blank=False
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='backend/',
        blank=True
    )
    description = models.TextField(
        verbose_name='Текстовое описание',
        blank=True,
        null=True
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        symmetrical=True,
        related_name='recipe_ingredients',
        through='IngredientAmount'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes'
    )
    cooking_time = models.PositiveIntegerField(
        validators=[
            MinValueValidator(
                1,
                'Время приготовления блюда не может быть меньше 1 минуты.'
            )
        ]
    )

    def __str__(self):
        return self.name



class IngredientAmount(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients_amount',
        verbose_name='Рецепт',
        db_index=True

    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.PROTECT,
        related_name='ingredient_in_recipes',
        verbose_name='Ингредиент',
        db_index=True
    )
    amount = models.PositiveIntegerField(
        validators=[
            MinValueValidator(
                1,
                'Количество не может быть меньше 1'
            )
        ]
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredient_in_recipe'
            )
        ]

class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь',
        db_index=True
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт',
        db_index=True
    )

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.recipe.favorites_count += 1
            self.recipe.save()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.recipe.favorites_count -= 1
        self.recipe.save()
        super().delete(*args, **kwargs)

    def __str__(self):
        return f'{self.user.username} добавил {self.recipe.name} в избраннное'

    class Meta:
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_recipe_favorite'
            )
        ]
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'