from .models import Course, Lesson
from rest_framework import serializers
from users.models import User, Payment

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'description', 'preview', 'video_url', 'course']

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'payment_date', 'paid_course', 'paid_lesson',
                 'amount', 'payment_method', 'user']
        read_only_fields = ['payment_date', 'user']

class CourseSerializer(serializers.ModelSerializer):
    # Задание 1: Количество уроков
    lessons_count = serializers.SerializerMethodField()

    # Задание 3: Полный вывод уроков
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'preview', 'description', 'owner',
            'created_at', 'updated_at', 'lessons_count', 'lessons'
        ]

    # noinspection PyMethodMayBeStatic
    def get_lessons_count(self, obj):
        """Возвращает количество уроков в курсе"""
        return obj.lessons.count()

class UserProfileSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(many=True, read_only=True)  # история платежей

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'phone', 'city', 'avatar',
            'first_name', 'last_name', 'payments'
        ]
        read_only_fields = ['email']


