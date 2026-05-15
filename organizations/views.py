from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import TariffPlan, Organizations, Subscriptions, Branch
from .serializers import (
    TariffPlanSerializer, OrganizationSerializer,
    SubscriptionSerializer, BranchSerializer
)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class TariffPlanViewSet(viewsets.ReadOnlyModelViewSet):
    """ Barcha faol tariflarni ko'rish (Start, Basic, Pro...) """
    queryset = TariffPlan.objects.filter(is_active=True)
    serializer_class = TariffPlanSerializer
    permission_classes = [AllowAny] # Tariflarni hamma ko'rishi mumkin (Saytda ko'rsatish uchun)


class OrganizationLoginView(APIView):
    permission_classes = [] # Hamma kirishi mumkin (Login sahifasi)

    def post(self, request):
        phone = request.data.get('phone')
        password = request.data.get('password')

        # 1. Telefon raqami bo'yicha tashkilotni qidiramiz
        try:
            organization = Organizations.objects.get(phone=phone)
        except Organizations.DoesNotExist:
            return Response(
                {"detail": "Telefon raqami yoki parol xato!"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # 2. Parolni tekshiramiz (Agar modelda parolni oddiy saqlayotgan bo'lsangiz)
        if organization.password == password:
            # Muvaffaqiyatli kirdi
            serializer = OrganizationSerializer(organization)
            return Response({
                "message": "Muvaffaqiyatli kirdingiz",
                "organization": serializer.data
            }, status=status.HTTP_200_OK)
        else:
            # Parol xato
            return Response(
                {"detail": "Telefon raqami yoki parol xato!"},
                status=status.HTTP_401_UNAUTHORIZED
            )

class OrganizationViewSet(
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if not user.organization:
            return Organizations.objects.none()

        return Organizations.objects.filter(id=user.organization.id)

    def perform_create(self, serializer):
        org = serializer.save()


class BranchViewSet(viewsets.ModelViewSet):
    """ Mijoz o'z filiallarini (Branch) yaratadi va boshqaradi """
    serializer_class = BranchSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Faqat o'z tashkilotining filiallari ko'rinadi
        user = self.request.user
        if not user.organization:
            return Branch.objects.none()
        return Branch.objects.filter(organization=user.organization)

    def perform_create(self, serializer):
        # Userning employee profili orqali tashkilotni topamiz
        employee = getattr(self.request.user, 'employee', None)

        if employee and employee.organization:
            serializer.save(organization=employee.organization)
        # else:
        #     # Agar userda tashkilot bo'lmasa, tushunarli xato qaytaramiz
        #     from rest_framework.exceptions import ValidationError
        #     raise ValidationError({"detail": "Sizda tashkilot aniqlanmadi, filial yarata olmaysiz!"})


class SubscriptionViewSet(mixins.CreateModelMixin,
                          mixins.ListModelMixin,
                          viewsets.GenericViewSet):
    """ Mijoz faqat o'ziga tegishli obuna tarixini ko'radi """
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.organization:
            return Subscriptions.objects.none()
        return Subscriptions.objects.filter(organization=user.organization).order_by('-created_at')