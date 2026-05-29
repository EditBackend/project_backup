# from rest_framework import viewsets, status
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
# from django.db.models import Q
# from django.apps import apps
#
# # Modellarni import qilish
# from .models import (
#     CRMPipeline, CRMSource, CRMLostReason,
#     CRMLead, CRMActivity, CRMLeadsHistory, CRMLeadLost, CrmSection
# )
#
# # Serializerlarni import qilish
# from .serializers import (
#     CRMPipelineSerializer, CRMSourceSerializer,
#     CRMLeadSerializer, CRMActivitySerializer, CRMLeadLostSerializer,
#     CRMLeadsHistorySerializer, CrmSectionSerializer
# )
#
# class BaseCRMViewSet(viewsets.ModelViewSet):
#     """
#     Barcha CRM ViewSetlar uchun Ota-Klass.
#     """
#     permission_classes = [IsAuthenticated]
#
#     def get_queryset(self):
#         user = self.request.user
#         org = getattr(user, 'organization', None)
#
#         if not org and hasattr(user, 'employee') and user.employee:
#             org = getattr(user.employee, 'organization', None)
#
#         if user.is_superuser or not org:
#             return self.queryset.all().order_by('-created_at')
#
#         return self.queryset.filter(
#             Q(organization=org) | Q(organization__isnull=True)
#         ).order_by('-created_at')
#
#     def perform_create(self, serializer):
#         user = self.request.user
#         org = None
#
#         if hasattr(user, 'organization') and user.organization:
#             org = user.organization
#         elif hasattr(user, 'employee') and user.employee and getattr(user.employee, 'organization', None):
#             org = user.employee.organization
#
#         if not org:
#             try:
#                 org_models = apps.get_app_config('organizations').get_models()
#                 for model in org_models:
#                     first_obj = model.objects.first()
#                     if first_obj:
#                         org = first_obj
#                         break
#             except Exception:
#                 pass
#
#         serializer.save(organization=org, created_by=user)
#
#     def perform_update(self, serializer):
#         user = self.request.user
#         org = None
#
#         if hasattr(user, 'organization') and user.organization:
#             org = user.organization
#         elif hasattr(user, 'employee') and user.employee and getattr(user.employee, 'organization', None):
#             org = user.employee.organization
#
#         if not org:
#             try:
#                 org_models = apps.get_app_config('organizations').get_models()
#                 for model in org_models:
#                     first_obj = model.objects.first()
#                     if first_obj:
#                         org = first_obj
#                         break
#             except Exception:
#                 pass
#
#         serializer.save(
#             organization=org,
#             updated_by=user if hasattr(serializer.model, 'updated_by') else None
#         )
#
#
# # ==========================================
# #   1. CRM PIPELINE BO'LIMLARI (NABORLAR)
# # ==========================================
# class CrmSectionViewSet(viewsets.ModelViewSet):
#     queryset = CrmSection.objects.all()
#     serializer_class = CrmSectionSerializer
#     permission_classes = [IsAuthenticated]
#
#     def get_queryset(self):
#         user = self.request.user
#         org = getattr(user, 'organization', None)
#
#         if not org and hasattr(user, 'employee') and user.employee:
#             org = getattr(user.employee, 'organization', None)
#
#         if user.is_superuser or not org:
#             queryset = CrmSection.objects.all()
#         else:
#             queryset = CrmSection.objects.filter(
#                 Q(organization=org) | Q(organization__isnull=True)
#             )
#
#         pipeline_id = self.request.query_params.get('pipeline')
#         if pipeline_id:
#             queryset = queryset.filter(pipeline_id=pipeline_id)
#
#         return queryset.order_by('created_at')
#
#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#
#         user = request.user
#         org = None
#
#         if hasattr(user, 'organization') and user.organization:
#             org = user.organization
#         elif hasattr(user, 'employee') and user.employee and getattr(user.employee, 'organization', None):
#             org = user.employee.organization
#
#         if not org:
#             try:
#                 org_models = apps.get_app_config('organizations').get_models()
#                 for model in org_models:
#                     first_obj = model.objects.first()
#                     if first_obj:
#                         org = first_obj
#                         break
#             except Exception:
#                 pass
#
#         section = serializer.save(organization=org, created_by=user)
#         return_serializer = self.get_serializer(section)
#         return Response(return_serializer.data, status=status.HTTP_201_CREATED)
#
#     def perform_update(self, serializer):
#         #  serializer.model bo'lmasligi kerak!
#         #  serializer.Meta.model bo'lishi shart!
#         model_class = serializer.Meta.model
#         serializer.save(
#             updated_by=self.request.user if hasattr(model_class, 'updated_by') else None
#         )
# # ==========================================
# # 2. PIPELINE BOSHQARUVI
# # ==========================================
# class PipelineViewSet(BaseCRMViewSet):
#     queryset = CRMPipeline.objects.all()
#     serializer_class = CRMPipelineSerializer
#
#     def get_queryset(self):
#         user = self.request.user
#         org = getattr(user, 'organization', None)
#
#         if not org and hasattr(user, 'employee') and user.employee:
#             org = getattr(user.employee, 'organization', None)
#
#         if user.is_superuser or not org:
#             return CRMPipeline.objects.all().order_by('-created_at')
#
#         return CRMPipeline.objects.filter(
#             Q(organization=org) | Q(organization__isnull=True)
#         ).order_by('-created_at')
#
#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#
#         user = request.user
#         org = None
#
#         if hasattr(user, 'organization') and user.organization:
#             org = user.organization
#         elif hasattr(user, 'employee') and user.employee and getattr(user.employee, 'organization', None):
#             org = user.employee.organization
#
#         if not org:
#             try:
#                 org_models = apps.get_app_config('organizations').get_models()
#                 for model in org_models:
#                     first_obj = model.objects.first()
#                     if first_obj:
#                         org = first_obj
#                         break
#             except Exception:
#                 pass
#
#         pipeline = serializer.save(organization=org, created_by=user)
#         return_serializer = self.get_serializer(pipeline)
#         return Response(return_serializer.data, status=status.HTTP_201_CREATED)
#
#     def perform_destroy(self, instance):
#         instance.delete()
#
#
# class CRMSourceViewSet(BaseCRMViewSet):
#     queryset = CRMSource.objects.all()
#     serializer_class = CRMSourceSerializer
#
#
# class CRMLeadViewSet(BaseCRMViewSet):
#     queryset = CRMLead.objects.all()
#     serializer_class = CRMLeadSerializer
#
#     # 🌟 Obyektni olish mantiqini kechirimli qilamiz (404 xatosini yo'qotadi)
#     def get_object(self):
#         queryset = CRMLead.objects.all()
#
#         # URL'dan lid ID sini olamiz
#         lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
#         filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
#
#         # Uni global bazadan qidiramiz, topilmasa qat'iy 404 beradi
#         from django.shortcuts import get_object_or_404
#         obj = get_object_or_404(queryset, **filter_kwargs)
#
#         # Ruxsatlarni tekshirish
#         self.check_object_permissions(self.request, obj)
#         return obj
#
#     def perform_update(self, serializer):
#         # Eski holatni bazadan to'g'ridan-to'g'ri olamiz
#         old_instance = self.get_object()
#         old_pipeline = old_instance.pipeline
#
#         user = self.request.user
#         org = getattr(user, 'organization', None)
#
#         if not org and hasattr(user, 'employee') and user.employee:
#             org = getattr(user.employee, 'organization', None)
#
#         # Agar foydalanuvchida umuman tashkilot bo'lmasa, lidning o'zini tashkilotini saqlab qolamiz
#         if not org:
#             org = old_instance.organization
#
#         # Lidni yangilaymiz
#         updated_lead = serializer.save(
#             organization=org,
#             updated_by=user
#         )
#
#         # Yangi pipeline (ustun orqali serializer validatsiyasida o'zgargan bo'ladi)
#         new_pipeline = updated_lead.pipeline
#
#         # Agar pipeline (yoki bosqich) o'zgargan bo'lsa, tarixga yozamiz
#         if old_pipeline != new_pipeline:
#             CRMLeadsHistory.objects.create(
#                 organization=updated_lead.organization,
#                 created_by=user,
#                 lead=updated_lead,
#                 old_pipeline=old_pipeline,
#                 new_pipeline=new_pipeline
#             )
# class CRMActivityViewSet(BaseCRMViewSet):
#     queryset = CRMActivity.objects.all()
#     serializer_class = CRMActivitySerializer
#
#
# class CRMLeadsHistoryViewSet(viewsets.ModelViewSet):
#     serializer_class = CRMLeadsHistorySerializer
#     permission_classes = [IsAuthenticated]
#
#     def get_queryset(self):
#         employee = getattr(self.request.user, 'employee', None)
#         if employee and employee.organization:
#             return CRMLeadsHistory.objects.filter(lead__organization=employee.organization)
#         return CRMLeadsHistory.objects.none()
#
#     def perform_create(self, serializer):
#         employee = getattr(self.request.user, 'employee', None)
#         serializer.save(created_by=employee)
#
#
# class CRMLeadLostViewSet(BaseCRMViewSet):
#     queryset = CRMLeadLost.objects.all()
#     serializer_class = CRMLeadLostSerializer
#
#     def perform_create(self, serializer):
#         user = self.request.user
#         org = getattr(user, 'organization', None)
#
#         if not org and hasattr(user, 'employee') and user.employee:
#             org = getattr(user.employee, 'organization', None)
#
#         lost_record = serializer.save(organization=org, created_by=user)
#         lead = lost_record.lead
#         lead.status = 'lost'
#         lead.save(

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.apps import apps

# Modellarni import qilish
from .models import (
    CRMPipeline, CRMSource, CRMLostReason,
    CRMLead, CRMActivity, CRMLeadsHistory, CRMLeadLost, CrmSection
)

# Serializerlarni import qilish
from .serializers import (
    CRMPipelineSerializer, CRMSourceSerializer,
    CRMLeadSerializer, CRMActivitySerializer, CRMLeadLostSerializer,
    CRMLeadsHistorySerializer, CrmSectionSerializer
)


# =================================================================
#  UNIVERSAL BASE VIEWSET — HAMMA ILОВАLAR UCHUN ASOSIY KLASS
# =================================================================
# =================================================================
# 🌟 UNIVERSAL BASE VIEWSET — MUKAMMAL VARIANTI (Tashkilot xatosiz)
# =================================================================
class UniversalBaseViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def _get_organization_from_request(self):
        """ Frontend yuborgan ID ni yoki foydalanuvchining o'z tashkilotini aniqlash """
        request = self.request
        user = request.user

        # 1. Agar foydalanuvchining o'ziga to'g'ridan-to'g'ri organization ulangan bo'lsa
        if hasattr(user, 'organization') and user.organization:
            return user.organization

        # 2. Agar foydalanuvchi xodim (Employee) bo'lsa, uning profilidan tashkilotni olamiz
        # Boyagi model mosligi uchun har ikkala ehtimoliy related_name ni tekshiramiz
        if hasattr(user, 'employee') and user.employee and getattr(user.employee, 'organization', None):
            return user.employee.organization
        if hasattr(user, 'employee_profile') and user.employee_profile and getattr(user.employee_profile,
                                                                                   'organization', None):
            return user.employee_profile.organization

        # 3. Agar foydalanuvchida topilmasa, frontendchi so'rovda organization_id yuborganmi tekshiramiz
        org_id = request.data.get('organization') or request.data.get('organization_id')
        if org_id:
            try:
                Organization = apps.get_model('organizations', 'Organization')
                return Organization.objects.get(id=org_id)
            except Exception:
                pass

        # 4. Agar superadmin bo'lsa va hali hech qayerga ulanmagan bo'lsa, bazadagi birinchi tashkilotni ulaymiz
        try:
            Organization = apps.get_model('organizations', 'Organization')
            first_org = Organization.objects.first()
            if first_org:
                return first_org
        except Exception:
            pass

        return None

    def get_queryset(self):
        org = self._get_organization_from_request()
        # Agar superadmin bo'lsa yoki tashkilot topilmasa hamma narsani ko'rsatadi
        if self.request.user.is_superuser or not org:
            return self.queryset.all().order_by('-created_at')
        return self.queryset.filter(
            Q(organization=org) | Q(organization__isnull=True)
        ).order_by('-created_at')

    def perform_create(self, serializer):
        org = self._get_organization_from_request()

        # ️ BAZADA INTEGRITY ERROR BO'LMASLIGI UCHUN TEKSHIRUV:
        if not org:
            raise serializers.ValidationError({
                "organization": "Tizimda siz tegishli bo'lgan tashkilot aniqlanmadi. Profilingizni tekshiring."
            })

        serializer.save(organization=org, created_by=self.request.user)

    def perform_update(self, serializer):
        org = self._get_organization_from_request()
        model_class = serializer.instance.__class__

        kwargs = {}
        # Agar modelda organization maydoni bo'lsa va u bo'sh bo'lsa, yangilaymiz
        if hasattr(model_class, 'organization') and org:
            kwargs["organization"] = org

        if hasattr(model_class, 'updated_by'):
            kwargs["updated_by"] = self.request.user

        serializer.save(**kwargs)




# Eski ota-klass nomini saqlab qolamiz (yig'iqroq ko'rinishda)
class BaseCRMViewSet(UniversalBaseViewSet):
    pass
#   1. CRM PIPELINE BO'LIMLARI (NABORLAR)
class CrmSectionViewSet(UniversalBaseViewSet):
    queryset = CrmSection.objects.all()
    serializer_class = CrmSectionSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        pipeline_id = self.request.query_params.get('pipeline')
        if pipeline_id:
            queryset = queryset.filter(pipeline_id=pipeline_id)
        return queryset.order_by('created_at')



# 2. PIPELINE BOSHQARUVI
class PipelineViewSet(UniversalBaseViewSet):
    queryset = CRMPipeline.objects.all()
    serializer_class = CRMPipelineSerializer


class CRMSourceViewSet(UniversalBaseViewSet):
    queryset = CRMSource.objects.all()
    serializer_class = CRMSourceSerializer


class CRMLeadViewSet(UniversalBaseViewSet):
    queryset = CRMLead.objects.all()
    serializer_class = CRMLeadSerializer

    #  Eski murakkab get_object() ni olib tashlang va o'rniga DRF'ning o'ziga qo'yib bering:
    def get_object(self):
        # DRF o'zi UUID bo'yicha bazadan chiroyli topib beradi, ruxsatlarni ham tekshiradi
        return super().get_object()

    def perform_update(self, serializer):
        old_instance = self.get_object()
        old_pipeline = old_instance.pipeline

        org = self._get_organization_from_request()
        if not org:
            org = old_instance.organization

        updated_lead = serializer.save(
            organization=org,
            updated_by=self.request.user
        )

        new_pipeline = updated_lead.pipeline

        if old_pipeline != new_pipeline:
            CRMLeadsHistory.objects.create(
                organization=updated_lead.organization,
                created_by=self.request.user,
                lead=updated_lead,
                old_pipeline=old_pipeline,
                new_pipeline=new_pipeline
            )


class CRMActivityViewSet(UniversalBaseViewSet):
    queryset = CRMActivity.objects.all()
    serializer_class = CRMActivitySerializer


class CRMLeadsHistoryViewSet(viewsets.ModelViewSet):
    serializer_class = CRMLeadsHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        org = getattr(user, 'organization', None)
        if not org and hasattr(user, 'employee') and user.employee:
            org = getattr(user.employee, 'organization', None)

        if org:
            return CRMLeadsHistory.objects.filter(lead__organization=org)
        return CRMLeadsHistory.objects.none()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class CRMLeadLostViewSet(UniversalBaseViewSet):
    queryset = CRMLeadLost.objects.all()
    serializer_class = CRMLeadLostSerializer

    def perform_create(self, serializer):
        org = self._get_organization_from_request()
        lost_record = serializer.save(organization=org, created_by=self.request.user)
        lead = lost_record.lead
        lead.status = 'lost'
        lead.save()