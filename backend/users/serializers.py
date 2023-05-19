from rest_framework import serializers
from recipes.serializers import SmallRecipeSerializer
from users.models import Subscription, User


class CustomUserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя"""
    password = serializers.CharField(write_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name', 'password',
            'is_subscribed'
        )
        write_only_fields = ('password',)

    def get_is_subscribed(self, obj):
        """Статус подписки на пользователя."""
        user_id = self.context.get('request').user.id
        return Subscription.objects.filter(
            author=obj.id,
            user=user_id
        ).exists()

    def create(self, validated_data):
        """Создание нового пользователя."""
        user = User.objects.create(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class SubscriptionSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    email = serializers.ReadOnlyField(source='author.email')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(source='author.recipes.count')
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'recipes',
            'recipes_count',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        """Статус подписки на пользователя."""
        user = self.context.get('request').user
        return Subscription.objects.filter(
            author=obj.author, user=user).exists()

    def get_recipes(self, obj):
        """Получение рецептов пользователя."""
        limit = self.context.get('request').GET.get('recipes_limit')
        recipe_obj = obj.author.recipes.all()
        if limit:
            recipe_obj = recipe_obj[:int(limit)]
        serializer = SmallRecipeSerializer(recipe_obj, many=True)
        return serializer.data
