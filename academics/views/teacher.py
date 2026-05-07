from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema

from academics.models.teacher import TeacherSalaryRules, TeacherSalaryCalculations, TeacherSalaryPayments
from academics.serializers.teacher import (
    TeacherSalaryRulesSerializer, TeacherSalaryCalculationsSerializer, TeacherSalaryPaymentsSerializer
)
from audit.models import AuditLog, AuditAction, AuditEntityType


def _log_audit(request, entity_type, entity_id, action, old_data=None, new_data=None):
    AuditLog.objects.create(
        organization=request.user.organization,
        branch=getattr(request.user, 'branch', None),
        created_by=request.user,
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        old_data=old_data,
        new_data=new_data
    )


class BaseTeacherSalaryViewSet(viewsets.ModelViewSet):
    """
    SaaS (Multi-tenant) arxitekturasi uchun umumiy qatlam.
    Barcha ustoz oyliklari shu yerdan meros oladi va tashkilot filtrini avtomat qo'llaydi.
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        # 1. BOSHQA MAKTAB MA'LUMOTLARINI YASHIRISH (Xavfsizlik)
        if not self.request.user.organization:
            return self.queryset.none()
        return self.queryset.filter(organization=self.request.user.organization).order_by('-created_at')

    def perform_create(self, serializer):
        # 2. SAAS UCHUN MAJBURIY QO'SHILADIGAN MAYDONLAR
        instance = serializer.save(
            organization=self.request.user.organization,
            branch=getattr(self.request.user, 'branch', None),
            created_by=self.request.user
        )
        return instance


@extend_schema(tags=["Teacher Salary - Qoidalar"])
class TeacherSalaryRulesViewSet(BaseTeacherSalaryViewSet):
    queryset = TeacherSalaryRules.objects.all().select_related('teacher__user')
    serializer_class = TeacherSalaryRulesSerializer
    filterset_fields = ['teacher']

    def perform_create(self, serializer):
        rule = super().perform_create(serializer)
        _log_audit(self.request, AuditEntityType.OTHER, rule.id, AuditAction.CREATE,
                   new_data={"action": "Oylik qoidasi kiritildi", "teacher_id": str(rule.teacher_id)})


@extend_schema(tags=["Teacher Salary - Oylik Tabeli (Hisobotlar)"])
class TeacherSalaryCalculationsViewSet(BaseTeacherSalaryViewSet):
    queryset = TeacherSalaryCalculations.objects.all().select_related('teacher__user', 'group')
    serializer_class = TeacherSalaryCalculationsSerializer
    filterset_fields = ['teacher', 'group', 'calculation_month']

    # Izoh: Aslida bu hisobot har oy oxirida celery task (crontab) orqali avtomatik to'lishi kerak.
    # Lekin adminlar qo'lda ham hisoblab/tuzatib qo'yishi mumkin.
    def perform_create(self, serializer):
        calc = super().perform_create(serializer)
        _log_audit(self.request, AuditEntityType.OTHER, calc.id, AuditAction.CREATE,
                   new_data={"action": "Oylik qo'lda hisoblandi", "amount": str(calc.total_amount)})


@extend_schema(tags=["Teacher Salary - To'langan Maoshlar"])
class TeacherSalaryPaymentsViewSet(BaseTeacherSalaryViewSet):
    queryset = TeacherSalaryPayments.objects.all().select_related('teacher__user')
    serializer_class = TeacherSalaryPaymentsSerializer
    filterset_fields = ['teacher', 'payment_type']

    def perform_create(self, serializer):
        with transaction.atomic():
            payment = super().perform_create(serializer)
            # Shu joyda Asosiy kassa (Moliya) balansi minus qilinishi kerak bo'lishi mumkin. (Keyingi qadamlar uchun joy tashlab ketamiz)

        _log_audit(self.request, AuditEntityType.PAYMENT, payment.id, AuditAction.CREATE,
                   new_data={"action": "Ustozga maosh berildi", "amount": str(payment.amount)})