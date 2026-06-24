from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Subscription
# Create your views here.
from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from .models import Course, Lesson
from .permissions import IsModer, IsOwner, IsModerOrOwner
from .serializers import CourseSerializer, LessonSerializer
from rest_framework import generics
from users.serializers import UserProfileSerializer

from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .paginators import StandardResultsPagination
from users.models import Payment
from .serializers import PaymentSerializer
# ViewSet для Курсов (полный CRUD)
# ViewSet для Курсов


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class = StandardResultsPagination

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            return [IsAuthenticated(), IsOwner()]
        return [IsAuthenticated(), IsModerOrOwner()]

# Generic Views для Уроков (CRUD)
class LessonListCreateAPIView(generics.ListCreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    pagination_class = StandardResultsPagination

    def perform_create(self, serializer):
        # Дополнительная проверка: пользователь должен быть владельцем курса
        course_id = self.request.data.get('course')
        if course_id:
            course = get_object_or_404(Course, id=course_id)
            if course.owner != self.request.user and not self.request.user.groups.filter(name='moders').exists():
                raise PermissionDenied("Вы можете создавать уроки только в своих курсах")

        serializer.save(owner=self.request.user)

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsOwner()]  # оставляем
        return [IsAuthenticated(), IsModerOrOwner()]

# Только просмотр (GET)
class LessonListAPIView(generics.ListAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


# Просмотр одного урока (GET)
class LessonDetailAPIView(generics.RetrieveAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsModerOrOwner]

# Обновление урока (PUT/PATCH)
class LessonUpdateAPIView(generics.UpdateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsModerOrOwner]

# Удаление урока (DELETE) — только владелец
class LessonDestroyAPIView(generics.DestroyAPIView):
    queryset = Lesson.objects.all()
    permission_classes = [IsAuthenticated, IsOwner]


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    """Список платежей с фильтрацией и сортировкой"""
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]

    # Задание 4
    filterset_fields = ['paid_course', 'paid_lesson', 'payment_method']
    ordering_fields = ['payment_date']
    ordering = ['-payment_date']  # по умолчанию новые сверху

class SubscriptionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        course_id = request.data.get('course_id')
        course = get_object_or_404(Course, id=course_id)
        user = request.user

        subs_item = Subscription.objects.filter(user=user, course=course)

        if subs_item.exists():
            subs_item.delete()
            message = 'Подписка успешно удалена'
        else:
            Subscription.objects.create(user=user, course=course)
            message = 'Подписка успешно добавлена'

        return Response({"message": message}, status=status.HTTP_200_OK)