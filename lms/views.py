from django.shortcuts import render
from drf_spectacular.types import OpenApiTypes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Subscription
# Create your views here.
from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from .models import Course, Lesson
from .permissions import IsModer, IsOwner, IsModerOrOwner
from .serializers import CourseSerializer, LessonSerializer, PaymentCreateSerializer
from rest_framework import generics
from users.serializers import UserProfileSerializer

from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .paginators import StandardResultsPagination
from users.models import Payment
from .serializers import PaymentSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiResponse
from drf_spectacular.types import OpenApiTypes

from .services import PaymentService
# ====================== СОЗДАНИЕ ПЛАТЕЖА (Stripe) ======================
from .services import PaymentService   # ← добавь этот импорт

# ViewSet для Курсов (полный CRUD)
# ViewSet для Курсов

@extend_schema_view(
    list=extend_schema(summary="Список всех курсов", tags=["Курсы"]),
    retrieve=extend_schema(summary="Получить один курс", tags=["Курсы"]),
    create=extend_schema(summary="Создать курс (только владелец)", tags=["Курсы"]),
    update=extend_schema(summary="Обновить курс", tags=["Курсы"]),
    partial_update=extend_schema(summary="Частичное обновление курса", tags=["Курсы"]),
    destroy=extend_schema(summary="Удалить курс (только владелец)", tags=["Курсы"]),
)
class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class = StandardResultsPagination

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            return [IsAuthenticated(), IsOwner()]
        return [IsAuthenticated(), IsModerOrOwner()]


# ====================== УРОКИ ======================
@extend_schema_view(
    get=extend_schema(summary="Список уроков", tags=["Уроки"]),
    post=extend_schema(
        summary="Создать урок",
        description="Можно создавать только в своих курсах",
        tags=["Уроки"],
        responses={201: LessonSerializer}
    )
)
class LessonListCreateAPIView(generics.ListCreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    pagination_class = StandardResultsPagination

    def perform_create(self, serializer):
        course_id = self.request.data.get('course')
        if course_id:
            course = get_object_or_404(Course, id=course_id)
            if course.owner != self.request.user and not self.request.user.groups.filter(name='moders').exists():
                raise PermissionDenied("Вы можете создавать уроки только в своих курсах")

        serializer.save(owner=self.request.user)

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsOwner()]
        return [IsAuthenticated(), IsModerOrOwner()]


@extend_schema_view(get=extend_schema(summary="Получить один урок", tags=["Уроки"]))
class LessonDetailAPIView(generics.RetrieveAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsModerOrOwner]


@extend_schema_view(
    patch=extend_schema(summary="Обновить урок", tags=["Уроки"]),
    put=extend_schema(summary="Обновить урок (полностью)", tags=["Уроки"])
)
class LessonUpdateAPIView(generics.UpdateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsModerOrOwner]


@extend_schema_view(delete=extend_schema(summary="Удалить урок (только владелец)", tags=["Уроки"]))
class LessonDestroyAPIView(generics.DestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsOwner]


# ====================== ПЛАТЕЖИ ======================
@extend_schema_view(list=extend_schema(summary="Список платежей", tags=["Платежи"]))
class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['paid_course', 'paid_lesson', 'payment_method']
    ordering_fields = ['payment_date']
    ordering = ['-payment_date']



# ====================== СОЗДАНИЕ ПЛАТЕЖА (Stripe) ======================
@extend_schema_view(
    post=extend_schema(
        summary="Создать платеж через Stripe",
        description="""
        Создаёт продукт и цену в Stripe, затем генерирует сессию оплаты.<br>
        Возвращает ссылку, по которой пользователь может оплатить курс.
        """,
        tags=["Платежи"],
        request=PaymentCreateSerializer,
        responses={
            201: OpenApiResponse(
                description="Платёж успешно создан",
                response={
                    "type": "object",
                    "properties": {
                        "payment_id": {"type": "integer", "example": 42},
                        "payment_link": {"type": "string", "example": "https://checkout.stripe.com/..."},
                        "message": {"type": "string", "example": "Перейдите по ссылке для оплаты"}
                    }
                }
            ),
            400: OpenApiResponse(description="Не указан course_id или курс не найден"),
            404: OpenApiResponse(description="Курс не найден"),
        }
    )
)
class PaymentCreateAPIView(generics.CreateAPIView):
    serializer_class = PaymentCreateSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        course_id = request.data.get('course_id')
        if not course_id:
            return Response({"error": "Поле course_id обязательно"}, status=status.HTTP_400_BAD_REQUEST)

        payment = PaymentService.create_payment(
            user=request.user,
            course_id=course_id
        )

        return Response({
            "payment_id": payment.id,
            "payment_link": payment.payment_link,
            "message": "Платёж успешно создан. Перейдите по ссылке для оплаты."
        }, status=status.HTTP_201_CREATED)


# ====================== ПОДПИСКИ ======================
@extend_schema_view(
    post=extend_schema(
        summary="Переключение подписки на курс (toggle)",
        description="Если подписка есть — удаляет, если нет — создаёт.",
        tags=["Подписки"],
        request=OpenApiTypes.OBJECT,
        responses={
            200: OpenApiResponse(
                description="Успешное переключение подписки",
                response={"type": "object", "properties": {"message": {"type": "string"}}}
            ),
            404: OpenApiResponse(description="Курс не найден"),
        }
    )
)
class SubscriptionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        course_id = request.data.get('course_id')
        course = get_object_or_404(Course, id=course_id)
        user = request.user

        subs_item = Subscription.objects.filter(user=user, course=course)

        if subs_item.exists():
            subs_item.delete()
            message = 'Подписка успешно удалена'
        else:
            Subscription.objects.create(user=user, course=course)
            message = 'Подписка успешно добавлена'

        return Response({"message": message}, status=status.HTTP_200_OK)

