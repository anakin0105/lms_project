from rest_framework.generics import CreateAPIView

from lms.permissions import IsOwner
from users.serializers import UserProfileSerializer, UserSerializer
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from users.models import User


# Create your views here.
class UserCreateAPIView(CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    def perform_create(self, serializer):
        user = serializer.save(is_active=True)
        user.set_password(user.password)
        user.save()

class UserProfileUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    lookup_field = 'id'

    def get_permissions(self):
        """
        GET → любой авторизованный пользователь
        PATCH/PUT → только владелец профиля
        """
        if self.request.method in ['GET']:  # только чтение
            return [IsAuthenticated()]

        # Редактирование и удаление
        return [IsAuthenticated(), IsOwner()]

    # Опционально: можно добавить perform_update, если нужно
    # def perform_update(self, serializer):
    #     serializer.save()