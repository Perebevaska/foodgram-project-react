from users.models import User
from rest_framework import serializers
from recipes.models import Tag, Ingredient, Recipe
from djoser.serializers import UserCreateSerializer, UserSerializer

#get
class UserGetSerializer(UserSerializer):

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name')
#post
class CustomUserSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        """Создание пользователя."""
        user = User.objects.create(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'password'
        )
        write_only_fields = ('password',)



class TagsSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с тэгами."""
    class Meta:
        model = Tag
        fields = '__all__'

class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с ингредиентами."""
    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с рецептами."""
    class Meta:
        model = Recipe
        fields = '__all__'