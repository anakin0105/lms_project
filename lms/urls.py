from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CourseViewSet, LessonListCreateAPIView, UserProfileUpdateAPIView, LessonRetrieveUpdateDestroyAPIView, PaymentViewSet

router = DefaultRouter()
router.register(r'courses', CourseViewSet)
router.register(r'payments', PaymentViewSet)

urlpatterns = [
    path('', include(router.urls)),

    # Уроки
    path('lessons/', LessonListCreateAPIView.as_view(), name='lesson-list-create'),
    path('lessons/<int:pk>/', LessonRetrieveUpdateDestroyAPIView.as_view(), name='lesson-detail'),

    # Профиль пользователя
    path('users/<int:id>/', UserProfileUpdateAPIView.as_view(), name='user-profile'),
]