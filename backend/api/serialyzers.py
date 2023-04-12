from rest_framework import serializers
from ..users.models import User
from django.contrib.auth.validators import UnicodeUsernameValidator
from ..users.validators import validate_me_name



class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=255,
        required=True,
        validators=[UnicodeUsernameValidator(), validate_me_name],
    )
    password = serializers.CharField(
        max_length=255,
        required=True
    )
    email = serializers.EmailField(
        required=True,
        max_length=50,
    )
    first_name = serializers.CharField(
        max_length=255,
        required=True
    )
    last_name = serializers.CharField(
        max_length=255,
        required=True
    )


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
