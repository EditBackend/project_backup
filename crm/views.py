from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import (
    CRMPipeline, CRMSource, CRMLostReason,
    CRMLead, CRMActivity, CRMLeadsHistory, CRMLeadLost
)
from .serializers import (
    CRMPipelineSerializer, CRMSourceSerializer,
    CRMLeadSerializer, CRMActivitySerializer, CRMLeadLostSerializer
)


class BaseCRMViewSet(viewsets.ModelViewSet):
    """
    Barcha CRM ViewSetlar uchun Ota-Klass.
    Bu xavfsizlikni bitta joydan boshqarish imkonini beradi.
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.organization:
            return self.queryset.none()
        return self.queryset.filter(organization=user.organization).order_by('-created_at')

    def perform_create(self, serializer):
        # Yaratilayotgan obyektga kimligi va qaysi tashkilotdanligini majburan yopishtiramiz
        serializer.save(
            organization=self.request.user.organization,
            created_by=self.request.user
        )


# Lug'atlar (Faqat o'z tashkilotidagilarni ko'radi va yaratadi)
class CRMPipelineViewSet(BaseCRMViewSet):
    queryset = CRMPipeline.objects.all()
    serializer_class = CRMPipelineSerializer


class CRMSourceViewSet(BaseCRMViewSet):
    queryset = CRMSource.objects.all()
    serializer_class = CRMSourceSerializer


# Asosiy Lidlar boshqaruvi
class CRMLeadViewSet(BaseCRMViewSet):
    queryset = CRMLead.objects.all()
    serializer_class = CRMLeadSerializer

    def perform_update(self, serializer):
        # 1. Eski ma'lumotni bazadan olamiz (O'zgartirishdan oldin)
        old_instance = self.get_object()
        old_pipeline = old_instance.pipeline

        # 2. Yangilangan ma'lumotni saqlaymiz
        updated_lead = serializer.save(updated_by=self.request.user)
        new_pipeline = updated_lead.pipeline

        # 3. Mantiq: Agar Pipeline (Bosqich) o'zgargan bo'lsa, Tarixga yozib qo'yamiz
        if old_pipeline != new_pipeline:
            CRMLeadsHistory.objects.create(
                organization=updated_lead.organization,
                created_by=self.request.user,
                lead=updated_lead,
                old_pipeline=old_pipeline,
                new_pipeline=new_pipeline
            )


# Harakatlar (Qo'ng'iroq va uchrashuvlar)
class CRMActivityViewSet(BaseCRMViewSet):
    queryset = CRMActivity.objects.all()
    serializer_class = CRMActivitySerializer


# Lidni rad etish (Lost)
class CRMLeadLostViewSet(BaseCRMViewSet):
    queryset = CRMLeadLost.objects.all()
    serializer_class = CRMLeadLostSerializer

    def perform_create(self, serializer):
        lost_record = serializer.save(
            organization=self.request.user.organization,
            created_by=self.request.user
        )
        # Lidning umumiy statusini ham 'lost' ga o'zgartirib qo'yamiz
        lead = lost_record.lead
        lead.status = 'lost'
        lead.save()