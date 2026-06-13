from rest_framework.serializers import ModelSerializer

from rest_framework import serializers
from lms.serializers import PaymentSerializer
from users.models import User


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class UserProfileSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'phone', 'city', 'avatar',
                  'first_name', 'last_name', 'payments']
        read_only_fields = ['email']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')

        # Если это НЕ владелец профиля — скрываем платежи
        if request and request.user != instance:
            data.pop('payments', None)
            # можно скрыть и другие поля при желании
        return data