from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import TariffPlan, Organizations, Subscriptions, Branch
from .serializers import (
    TariffPlanSerializer, OrganizationSerializer,
    SubscriptionSerializer, BranchSerializer
)

class TariffPlanViewSet(viewsets.ReadOnlyModelViewSet):
    """ Barcha faol tariflarni ko'rish (Start, Basic, Pro...) """
    queryset = TariffPlan.objects.filter(is_active=True)
    serializer_class = TariffPlanSerializer
    permission_classes = [AllowAny] # Tariflarni hamma ko'rishi mumkin (Saytda ko'rsatish uchun)


class OrganizationViewSet(mixins.RetrieveModelMixin,
                          mixins.UpdateModelMixin,
                          mixins.ListModelMixin,
                          viewsets.GenericViewSet):
    """ Mijoz FAQAAT o'z tashkilotini ko'radi va tahrirlaydi """
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # IDOR HIMOYASI: Faqatgina o'z tashkilotini qaytaramiz
        user = self.request.user
        if not user.organization:
            return Organizations.objects.none()
        return Organizations.objects.filter(id=user.organization.id)


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
        # XAVFSIZLIK: Yangi filial yaratilganda uni avtomatik joriy foydalanuvchining tashkilotiga bog'laymiz
        serializer.save(organization=self.request.user.organization)


class SubscriptionViewSet(viewsets.ReadOnlyModelViewSet):
    """ Mijoz faqat o'ziga tegishli obuna tarixini ko'radi """
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.organization:
            return Subscriptions.objects.none()
        return Subscriptions.objects.filter(organization=user.organization).order_by('-created_at')