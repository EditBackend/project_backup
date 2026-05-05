from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from .models import AuditLog
from .serializers import AuditLogSerializer


@extend_schema(tags=["AuditLog - Barcha bajarilgan ishlarni ko'rish"])
class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Faqat O'QISH uchun mo'ljallangan ViewSet.
    Hech kim audit jurnalini tahrirlay yoki o'chira olmaydi.
    """
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated]

    # Qidiruv va filtrlash
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['action', 'entity_type']
    search_fields = ['performed_by_role', 'created_by__full_name']

    def get_queryset(self):
        user = self.request.user

        # 1. Tashkilotsiz userlarga hech narsa ko'rsatmaymiz
        if not user.organization:
            return AuditLog.objects.none()

        # 2. XAVFSIZLIK: Faqat O'Z tashkilotidagi tarixlarni ko'radi
        # select_related orqali User jadvalini oldindan olib kelamiz (N+1 ni oldini olish uchun)
        return AuditLog.objects.filter(
            organization=user.organization
        ).select_related('created_by').order_by('-created_at')