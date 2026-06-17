from django.db import models

# Create your models here.
from django.db import models
from users.models import User


class Course(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название курса")
    preview = models.ImageField(upload_to='course_previews/', blank=True, null=True, verbose_name="Превью")
    description = models.TextField(verbose_name="Описание курса")

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='courses',
        verbose_name="Владелец"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Lesson(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='lessons',
        verbose_name="Курс"
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='lessons',
        verbose_name="Владелец"
    )
    title = models.CharField(max_length=200, verbose_name="Название урока")
    description = models.TextField(verbose_name="Описание урока")
    preview = models.ImageField(upload_to='lesson_previews/', blank=True, null=True, verbose_name="Превью")
    video_url = models.URLField(blank=True, null=True, verbose_name="Ссылка на видео")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"
        ordering = ['id']

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name="Пользователь"
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name="Курс"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата подписки")

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        unique_together = ('user', 'course')  # гарантия уникальности
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} → {self.course.title}"