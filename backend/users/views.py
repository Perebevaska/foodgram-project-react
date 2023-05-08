from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.serializers import SubscriptionSerializer

from .models import Subscription, User


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()

    @action(
        detail=False,
        url_path='subscriptions',
        url_name='subscriptions',
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        """Список пользователей, на которых подписан пользователь."""
        user = request.user
        queryset = user.follower.all()
        pages = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(
            pages, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(
        methods=['post', 'delete'],
        detail=True,
        url_path='subscribe',
        url_name='subscribe',
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, id=None):
        """Подписка на автора рецепта."""
        user = request.user
        author = get_object_or_404(User, id=id)
        if user == author:
            raise ValidationError('На себя нельзя подписаться / отписаться')
        subscription = Subscription.objects.filter(
            author=author, user=user)
        if request.method == 'POST':
            subscription, created = Subscription.objects.get_or_create(
                author=author,
                user=user
            )
            if not created:
                raise ValidationError('Нельзя подписаться повторно')
            serializer = SubscriptionSerializer(
                subscription,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            subscription = Subscription.objects.filter(
                author=author,
                user=user
            ).first()
            if not subscription:
                raise ValidationError(
                    'Нельзя отписаться от неподписанного автора'
                )
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise ValidationError('Метод не поддерживается')
