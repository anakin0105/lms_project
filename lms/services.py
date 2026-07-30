import stripe
from django.shortcuts import get_object_or_404

from config.settings import STRIPE_API_KEY
from forex_python.converter import CurrencyRates

from lms.models import Course
from users.models import Payment

stripe.api_key = STRIPE_API_KEY
print("STRIPE KEY:", stripe.api_key[:10])


class PaymentService:
    """Сервис для интеграции со Stripe (современный подход 2025-2026)"""

    @staticmethod
    def create_payment(user, course_id: int, amount: int = None):
        """
        Основная функция создания платежа
        """
        course = get_object_or_404(Course, id=course_id)

        # Если сумму не передали — берём 1500 руб (потом можно добавить поле price в Course)
        if not amount:
            amount = 1500

        try:
            # 1. Создаём продукт в Stripe
            product = stripe.Product.create(
                name=course.title,
                description=f"Оплата курса: {course.title}",
                metadata={"course_id": course.id}
            )

            # 2. Создаём цену (обязательно в копейках!)
            price = stripe.Price.create(
                unit_amount=int(amount * 100),   # 1500 руб = 150000 копеек
                currency="rub",
                product=product.id,
            )

            # 3. Создаём сессию Checkout
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price': price.id,
                    'quantity': 1,
                }],
                mode='payment',
                success_url="http://127.0.0.1:8000/api/payment/success/?session_id={CHECKOUT_SESSION_ID}",
                cancel_url="http://127.0.0.1:8000/api/payment/cancel/",
                metadata={
                    'user_id': str(user.id),
                    'course_id': str(course.id),
                    'payment_type': 'course'
                }
            )

            # 4. Сохраняем платёж в базе
            payment = Payment.objects.create(
                user=user,
                paid_course=course,
                amount=amount,
                stripe_product_id=product.id,
                stripe_price_id=price.id,
                stripe_session_id=session.id,
                payment_link=session.url,
                status='pending'
            )

            return payment

        except stripe.error.StripeError as e:
            print(f"Stripe Error: {str(e)}")
            raise Exception(f"Ошибка Stripe: {str(e)}")


    @staticmethod
    def retrieve_session(session_id):
        """Дополнительно: проверка статуса платежа"""
        return stripe.checkout.Session.retrieve(session_id)