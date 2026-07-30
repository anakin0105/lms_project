from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta

from .models import Course, Subscription


@shared_task
def send_course_update_notification(course_id: int):
    """Задача: отправка уведомления подписчикам об обновлении курса"""
    try:
        course = Course.objects.get(id=course_id)

        # Дополнительное задание: проверяем, обновлялся ли курс более 4 часов назад
        if course.updated_at and (timezone.now() - course.updated_at) < timedelta(hours=4):
            print(f"Уведомление для курса {course.title} пропущено (обновление было недавно)")
            return

        subscribers = Subscription.objects.filter(course=course).select_related('user')

        if not subscribers.exists():
            return

        subject = f"Обновление в курсе: {course.title}"
        message = f"""
        Здравствуйте!

        В курсе "{course.title}" появились обновления.

        Перейдите в платформу, чтобы посмотреть новые материалы.

        С уважением,
        Команда LMS
        """

        recipient_list = [sub.user.email for sub in subscribers if sub.user.email]

        send_mail(
            subject=subject,
            message=message,
            from_email=None,  # использует DEFAULT_FROM_EMAIL
            recipient_list=recipient_list,
            fail_silently=False,
        )

        print(f"✅ Уведомления отправлены {len(recipient_list)} подписчикам курса '{course.title}'")

    except Exception as e:
        print(f"❌ Ошибка при отправке уведомлений: {e}")


@shared_task
def deactivate_inactive_users():
    """Периодическая задача: блокировка пользователей, не заходивших > 1 месяца"""
    from django.contrib.auth import get_user_model
    User = get_user_model()

    one_month_ago = timezone.now() - timedelta(days=30)

    inactive_users = User.objects.filter(
        last_login__lt=one_month_ago,
        is_active=True
    )

    count = inactive_users.update(is_active=False)

    print(f"✅ Деактивировано {count} неактивных пользователей")