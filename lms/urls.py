from django.urls import path, include
from rest_framework.routers import DefaultRouter

from users.views import UserProfileUpdateAPIView
from .views import CourseViewSet, LessonListCreateAPIView, PaymentViewSet, \
    LessonDetailAPIView, LessonUpdateAPIView, LessonDestroyAPIView, SubscriptionAPIView

router = DefaultRouter()
router.register(r'courses', CourseViewSet)
router.register(r'payments', PaymentViewSet)

urlpatterns = [
    path('', include(router.urls)),

    # Уроки
    path('lessons/', LessonListCreateAPIView.as_view(), name='lesson-list-create'),
    path('lessons/<int:pk>/', LessonDetailAPIView.as_view(), name='lesson-detail'),
    path('lessons/<int:pk>/update/', LessonUpdateAPIView.as_view(), name='lesson-update'),
    path('lessons/<int:pk>/delete/', LessonDestroyAPIView.as_view(), name='lesson-delete'),
    path('subscribe/', SubscriptionAPIView.as_view(), name='subscribe'),

]