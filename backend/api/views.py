from rest_framework.decorators import action, api_view
from users.models import User
from .serialyzers import RegisterSerializer, UserSerializer
from rest_framework.serializers import ValidationError
from django.db import IntegrityError
from rest_framework.status import HTTP_201_CREATED
from rest_framework.response import Response
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from rest_framework import viewsets, status
from django.shortcuts import get_object_or_404





def send_confirmation_code(user):
    confirmation_code = default_token_generator.make_token(user)
    return send_mail(
        'Код подтверждения от yamdb',
        f'Код подтверждения:{confirmation_code}',
        'admin@admin.ru',
        [user.email],
        fail_silently=False
    )

# Create your views here.
@api_view(['POST'])
def sign_up(request):
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data.get('username')
    password = serializer.validated_data.get('password')
    email = serializer.validated_data.get('email')
    first_name = serializer.validated_data.get('first_name')
    last_name = serializer.validated_data.get('last_name')
    try:
        user, create = User.objects.get_or_create(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name
        )
    except IntegrityError as error:
        raise ValidationError(
            ('Ошибка при попытке создать новую запись '
             f'в базе с username={username}, email={email}')
        ) from error
    send_confirmation_code(user)
    return Response(serializer.validated_data, status=HTTP_201_CREATED)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_patch_me(self, request):
        user = get_object_or_404(User, username=self.request.user)
        if request.method == 'GET':
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == 'PATCH':
            serializer = UserSerializer(
                user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            if request.user.is_admin:
                serializer.save()
            else:
                serializer.save(role=request.user.role)
            return Response(serializer.data, status=status.HTTP_200_OK)