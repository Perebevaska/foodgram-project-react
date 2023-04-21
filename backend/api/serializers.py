from users.models import User
from rest_framework import serializers
from recipes.models import Tag, Ingredient, Recipe




class CustomUserSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True)
    def create(self, validated_data):
        """Создание пользователя."""
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return


    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'email', 'first_name','last_name')
        write_only_fields = ('password',)


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'

class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с ингредиентами."""
    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с ингредиентами."""
    class Meta:
        model = Recipe
        fields = '__all__'