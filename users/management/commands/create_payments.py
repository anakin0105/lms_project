from django.core.management.base import BaseCommand
from users.models import User, Payment
from lms.models import Course, Lesson


class Command(BaseCommand):
    help = 'Создаёт тестовые платежи'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Начинаем создание платежей...'))

        # Берём первого пользователя (или создаём, если нет)
        try:
            user = User.objects.first()
            if not user:
                user = User.objects.create_user(
                    username='testuser',
                    email='test@example.com',
                    password='password123'
                )
                self.stdout.write(self.style.SUCCESS(f'Создан тестовый пользователь: {user.email}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка с пользователем: {e}'))
            return

        # Берём курсы и уроки
        courses = Course.objects.all()
        lessons = Lesson.objects.all()

        # Создаём платежи
        payments_data = [
            {
                'user': user,
                'paid_course': courses.first() if courses.exists() else None,
                'paid_lesson': None,
                'amount': 2500.00,
                'payment_method': 'transfer'
            },
            {
                'user': user,
                'paid_course': None,
                'paid_lesson': lessons.first() if lessons.exists() else None,
                'amount': 800.00,
                'payment_method': 'cash'
            },
            {
                'user': user,
                'paid_course': courses.last() if courses.exists() else None,
                'paid_lesson': None,
                'amount': 1800.00,
                'payment_method': 'transfer'
            },
        ]

        for data in payments_data:
            Payment.objects.create(**data)
            self.stdout.write(self.style.SUCCESS(f'Создан платеж на сумму {data["amount"]}'))

        self.stdout.write(self.style.SUCCESS('✅ Платежи успешно созданы!'))