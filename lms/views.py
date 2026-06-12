from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, generics
from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer
from rest_framework import generics
from users.models import User
from .serializers import UserProfileSerializer
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend

from users.models import Payment
from .serializers import PaymentSerializer
# ViewSet для Курсов (полный CRUD)
class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer


# Generic Views для Уроков (CRUD)
class LessonListCreateAPIView(generics.ListCreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class LessonRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

# Дополнительное задание — Редактирование профиля пользователя
class UserProfileUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    lookup_field = 'id'   # можно будет обращаться по /api/users/5/


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    """Список платежей с фильтрацией и сортировкой"""
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]

    # Задание 4
    filterset_fields = ['paid_course', 'paid_lesson', 'payment_method']
    ordering_fields = ['payment_date']
    ordering = ['-payment_date']  # по умолчанию новые сверху