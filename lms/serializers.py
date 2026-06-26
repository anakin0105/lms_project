from .models import Course, Lesson
from rest_framework import serializers
from users.models import User, Payment
from .validators import youtube_validator

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'description', 'preview', 'video_url', 'course']
        extra_kwargs = {
            'video_url': {
                'validators': [youtube_validator]
            }
        }

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
    is_subscribed = serializers.SerializerMethodField()  # ← новое

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'preview', 'description', 'owner',
            'created_at', 'updated_at', 'lessons_count', 'lessons', 'is_subscribed'
        ]
        read_only_fields = ['owner', 'created_at', 'updated_at']


    # noinspection PyMethodMayBeStatic
    def get_lessons_count(self, obj) -> int:
        """Возвращает количество уроков в курсе"""
        return obj.lessons.count()

    def get_is_subscribed(self, obj) -> bool:
        """Проверяет, подписан ли текущий пользователь на курс"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.subscriptions.filter(user=request.user).exists()

class PaymentCreateSerializer(serializers.Serializer):
    """Схема для запроса на создание платежа"""
    course_id = serializers.IntegerField(help_text="ID курса для оплаты")
    # lesson_id = serializers.IntegerField(required=False, help_text="ID урока (опционально)")