from rest_framework import serializers
from ..users.models import User

from dj_rest_auth.registration.serializers import RegisterSerializer

class CustomRegisterSerializer(RegisterSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    def get_cleaned_data(self):
        super().get_cleaned_data()
        self.cleaned_data['first_name'] = self.validated_data.get('first_name', '')
        self.cleaned_data['last_name'] = self.validated_data.get('last_name', '')
        return self.cleaned_data



#модифицировать с этим
    class Meta:
        model = User
        fields = '__all__'

        class SignUpSerializer(serializers.Serializer):
            email = serializers.EmailField(
                required=True, max_length=settings.LEN_EMAIL, )
            username = serializers.CharField(
                max_length=settings.USER_LEN_NAME,
                required=True,
                validators=[UnicodeUsernameValidator(), validate_me_name],
            )
