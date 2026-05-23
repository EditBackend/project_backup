from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
# 'Pipeline' o'rniga 'CRMPipeline' deb import qilamiz:
from crm.models import CRMPipeline
from .models import (
    CRMPipeline, CRMSource, CRMLostReason,
    CRMLead, CRMActivity, CRMLeadsHistory, CRMLeadLost,CrmSection
)
from .serializers import (
    CRMPipelineSerializer, CRMSourceSerializer,
    CRMLeadSerializer, CRMActivitySerializer, CRMLeadLostSerializer,CRMLeadsHistorySerializer,CrmSectionSerializer
)

class CrmSectionViewSet(viewsets.ModelViewSet):
    """
    CRM Pipeline bo'limlari (Naborlar) uchun API.
    """
    queryset = CrmSection.objects.all().order_by('-created_at')
    serializer_class = CrmSectionSerializer

    def get_queryset(self):
        queryset = self.queryset
        pipeline_id = self.request.query_params.get('pipeline')

        # Agar pipeline_id kelgan bo'lsa, faqat o'sha pipeline'ga tegishli sectionlarni chiqaramiz
        if pipeline_id:
            queryset = queryset.filter(pipeline_id=pipeline_id)

        return queryset
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


class PipelineViewSet(BaseCRMViewSet):
    """
    Pipeline boshqaruvi.
    Frontenddan organization ID kelsa ham, kelmasa ham xatosiz POST qiladi va yo'qotib qo'ymaydi.
    """
    # 🌟 O'chib ketgan queryset'ni majburiy biriktiramiz:
    queryset = CRMPipeline.objects.all()
    serializer_class = CRMPipelineSerializer

    # ==========================================
    # 1. MA'LUMOTLARNI FILTERLASH (GET) - YO'QOLMAYDIGAN VARIANT
    # ==========================================
    def get_queryset(self):
        user = self.request.user
        org = getattr(user, 'organization', None)

        # Agar userning o'zida tashkilot bo'lmasa, uning employee profilini ham tekshirib ko'ramiz
        if not org and hasattr(user, 'employee') and user.employee:
            org = getattr(user.employee, 'organization', None)

        # Superuser bo'lsa yoki test user bo'lsa (tashkiloti yo'q bo'lsa), hamma narsani ko'rsatsin, yo'qolib qolmasligi uchun
        if user.is_superuser or not org:
            return CRMPipeline.objects.all().order_by('-created_at')

        from django.db.models import Q
        # Agar haqiqiy tashkiloti bo'lsa, faqat o'ziga tegishlilarini ko'radi
        return CRMPipeline.objects.filter(
            Q(organization=org) | Q(organization__isnull=True)
        ).order_by('-created_at')

    # ==========================================
    # 2. YANGI PIPELINE YARATISH (POST)
    # ==========================================
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        org = None

        # 1. Foydalanuvchining o'zidan qidiramiz
        if hasattr(user, 'organization') and user.organization:
            org = user.organization
        # 2. Xodim profili ichidan qidiramiz
        elif hasattr(user, 'employee') and user.employee and getattr(user.employee, 'organization', None):
            org = user.employee.organization

        # 3. Agar topilmasa, dinamik qidiramiz
        if not org:
            from django.apps import apps
            try:
                org_models = apps.get_app_config('organizations').get_models()
                for model in org_models:
                    first_obj = model.objects.first()
                    if first_obj:
                        org = first_obj
                        break
            except Exception:
                pass

        # Obyektni saqlaymiz
        pipeline = serializer.save(
            organization=org,
            created_by=user
        )

        # Yangi yaratilgan obyektni bazadan toza holatda o'qib qaytaramiz
        return_serializer = self.get_serializer(pipeline)
        headers = self.get_success_headers(return_serializer.data)
        return Response(return_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    # 3. PIPELINE O'CHIRISH (DELETE)
    def perform_destroy(self, instance):
        instance.delete()
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
class CRMLeadsHistoryViewSet(viewsets.ModelViewSet):
    serializer_class = CRMLeadsHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Faqat foydalanuvchi tashkilotiga tegishli leadlar tarixini qaytaramiz
        employee = getattr(self.request.user, 'employee', None)
        if employee and employee.organization:
            return CRMLeadsHistory.objects.filter(lead__organization=employee.organization)
        return CRMLeadsHistory.objects.none()

    def perform_create(self, serializer):
        # Yaratuvchini avtomatik employee sifatida saqlaymiz
        employee = getattr(self.request.user, 'employee', None)
        serializer.save(created_by=employee)

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