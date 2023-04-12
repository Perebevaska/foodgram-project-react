from django.shortcuts import render
from rest_framework.decorators import action, api_view
from users.models import User
from rest_framework.serializers import ValidationError
from django.db import IntegrityError
from rest_framework.status import HTTP_201_CREATED
from rest_framework.response import Response
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail


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