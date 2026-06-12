from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated

from .models import Course, Lesson
from .permissions import IsModer, IsOwner
from .serializers import CourseSerializer, LessonSerializer
from rest_framework import generics
from users.serializers import UserProfileSerializer

from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend

from users.models import Payment
from .serializers import PaymentSerializer
# ViewSet для Курсов (полный CRUD)
class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            return [IsAuthenticated(), IsOwner()]
        # Для update, list, retrieve — модератор или владелец
        return [IsAuthenticated(), IsModer | IsOwner]

# Generic Views для Уроков (CRUD)
class LessonListCreateAPIView(generics.ListCreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = (IsAuthenticated,)


    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_permissions(self):
        if self.request.method == 'POST':           # create
            return [IsAuthenticated(), IsOwner()]  # только владелец (немодератор)
        return [IsAuthenticated(), IsModer | IsOwner]  # list — модератор или владелец


# Только просмотр (GET)
class LessonListAPIView(generics.ListAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


# Просмотр одного урока (GET)
class LessonDetailAPIView(generics.RetrieveAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsModer | IsOwner]

# Обновление урока (PUT/PATCH) — тут нужен модератор
class LessonUpdateAPIView(generics.UpdateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsModer | IsOwner]

# Удаление урока (DELETE) — запрещаем модератору
class LessonDestroyAPIView(generics.DestroyAPIView):
    queryset = Lesson.objects.all()
    permission_classes = [IsAuthenticated, IsOwner]   # ← модератор НЕ должен удалять!


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    """Список платежей с фильтрацией и сортировкой"""
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]

    # Задание 4
    filterset_fields = ['paid_course', 'paid_lesson', 'payment_method']
    ordering_fields = ['payment_date']
    ordering = ['-payment_date']  # по умолчанию новые сверху