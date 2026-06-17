from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from lms.models import Course, Lesson, Subscription

User = get_user_model()


class LessonTestCase(APITestCase):
    """Тесты для уроков"""

    def setUp(self):
        self.user_owner = User.objects.create_user(
            username="owner_test", email="owner@test.com", password="testpass123"
        )
        self.user_moder = User.objects.create_user(
            username="moder_test", email="moder@test.com", password="testpass123"
        )
        self.user_regular = User.objects.create_user(
            username="regular_test", email="regular@test.com", password="testpass123"
        )

        from django.contrib.auth.models import Group
        moder_group, _ = Group.objects.get_or_create(name='moders')
        self.user_moder.groups.add(moder_group)

        self.course = Course.objects.create(
            title="Тестовый курс", description="Описание", owner=self.user_owner
        )

        self.lesson = Lesson.objects.create(
            title="Тестовый урок",
            description="Описание урока",
            course=self.course,
            owner=self.user_owner,
            video_url="https://www.youtube.com/watch?v=test"
        )

        self.client.force_authenticate(user=self.user_owner)

    def test_lesson_create(self):
        url = reverse('lesson-list-create')
        data = {
            "title": "Новый урок",
            "description": "Новое описание",
            "course": self.course.pk,
            "video_url": "https://youtu.be/dQw4w9wgxcq"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_lesson_create_invalid_youtube(self):
        url = reverse('lesson-list-create')
        data = {
            "title": "Плохой урок",
            "description": "Описание",
            "course": self.course.pk,
            "video_url": "https://vk.com/bad"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_lesson_retrieve(self):
        url = reverse('lesson-detail', args=(self.lesson.pk,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_lesson_update_owner(self):
        url = reverse('lesson-update', args=(self.lesson.pk,))
        data = {"title": "Обновлённый урок"}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_lesson_delete_owner(self):
        url = reverse('lesson-delete', args=(self.lesson.pk,))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_regular_user_cannot_create(self):
        self.client.force_authenticate(user=self.user_regular)
        url = reverse('lesson-list-create')
        data = {"title": "Чужой", "description": "123", "course": self.course.pk}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_moder_can_update(self):
        self.client.force_authenticate(user=self.user_moder)
        url = reverse('lesson-update', args=(self.lesson.pk,))
        response = self.client.patch(url, {"title": "Модератор обновил"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_subscription_toggle(self):
        self.client.force_authenticate(user=self.user_regular)
        url = reverse('subscribe')
        data = {'course_id': self.course.pk}

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Подписка успешно добавлена')


class CourseTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="course_test", email="course@test.com", password="testpass123"
        )
        self.client.force_authenticate(user=self.user)
        self.course = Course.objects.create(
            title="Курс для теста", description="Описание", owner=self.user
        )

    def test_course_list_has_is_subscribed(self):
        url = reverse('course-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn('is_subscribed', data['results'][0])