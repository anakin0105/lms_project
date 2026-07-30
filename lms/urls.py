from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CourseViewSet,
    LessonListCreateAPIView,
    LessonDetailAPIView,
    LessonUpdateAPIView,
    LessonDestroyAPIView,
    SubscriptionAPIView,
    PaymentViewSet,
    PaymentCreateAPIView
)

router = DefaultRouter()
router.register(r'courses', CourseViewSet)
router.register(r'payments', PaymentViewSet)   # только для списка платежей (GET)

urlpatterns = [
    # ВОТ СЮДА — до роутера!
    path('payments/create/', PaymentCreateAPIView.as_view(), name='payment-create'),

    path('', include(router.urls)),

    path('lessons/', LessonListCreateAPIView.as_view(), name='lesson-list-create'),
    path('lessons/<int:pk>/', LessonDetailAPIView.as_view(), name='lesson-detail'),
    path('lessons/<int:pk>/update/', LessonUpdateAPIView.as_view(), name='lesson-update'),
    path('lessons/<int:pk>/delete/', LessonDestroyAPIView.as_view(), name='lesson-delete'),
    path('subscribe/', SubscriptionAPIView.as_view(), name='subscribe'),
]