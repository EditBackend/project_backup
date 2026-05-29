from decimal import Decimal, InvalidOperation
from django.db import transaction
from django.db.models import Prefetch, F
from django.shortcuts import get_object_or_404
from django.apps import apps
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action
from rest_framework_simplejwt.views import TokenObtainPairView

# Asosiy universal ViewSet (Agar alohida utilsda bo'lsa, o'sha yerdan import qiling)
from crm.views import UniversalBaseViewSet

from academics.models import (
    Student, StudentGroup, StudentBalances, StudentTransaction,
    StudentGroupLeaves, StudentFreezes, StudentPricing, LeaveReason, StudentBalanceHistory
)
from academics.serializers.student import (
    StudentSerializer, StudentTransactionSerializer, StudentFreezeSerializer,
    StudentPricingSerializer, StudentGroupSerializer, LeaveReasonSerializer,
    StudentBalanceHistorySerializer, StudentBalanceSerializer, StudentGroupLeavesSerializer
)
from audit.models import AuditLog, AuditAction, AuditEntityType


# Tashkilotni har qanday foydalanuvchidan (Superadmin yoki Employee) xavfsiz olish
def _get_clean_org(user):
    if hasattr(user, 'organization') and user.organization:
        return user.organization
    if hasattr(user, 'employee') and user.employee and getattr(user.employee, 'organization', None):
        return user.employee.organization
    if hasattr(user, 'employee_profile') and user.employee_profile and getattr(user.employee_profile, 'organization', None):
        return user.employee_profile.organization
    try:
        Organization = apps.get_model('organizations', 'Organization')
        return Organization.objects.first()
    except Exception:
        return None

def _log_audit(request, entity_type, entity_id, action, old_data=None, new_data=None):
    user = request.user
    org = _get_clean_org(user)
    AuditLog.objects.create(
        organization=org,
        branch=getattr(user, 'branch', None),
        created_by=user,
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        old_data=old_data,
        new_data=new_data
    )

# 1. ASOSIY TALABALAR VIEWSETI
class StudentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = StudentSerializer
    queryset = Student.objects.all()

    def get_queryset(self):
        user = self.request.user
        org = _get_clean_org(user)

        if user.is_superuser or not org:
            return Student.objects.all().select_related('balance_info').order_by('-created_at')
        return Student.objects.filter(organization=org).select_related('balance_info').order_by('-created_at')

    def perform_create(self, serializer):
        user = self.request.user
        org = _get_clean_org(user)

        if not org:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"detail": "Siz biror bir tashkilotga biriktirilmagansiz!"})

        with transaction.atomic():
            student = serializer.save(
                organization=org,
                branch=getattr(user, 'branch', None),
                created_by=user
            )
            StudentBalances.objects.get_or_create(
                student=student,
                defaults={
                    'balance': Decimal('0'),
                    'organization': org,
                    'branch': getattr(user, 'branch', None)
                }
            )

        _log_audit(
            self.request,
            entity_type=AuditEntityType.STUDENT,
            entity_id=student.id,
            action=AuditAction.CREATE,
            new_data={"name": student.full_name, "phone": student.phone_number}
        )

    @action(detail=True, methods=['post'], url_path='add-to-group')
    def add_to_group(self, request, pk=None):
        student = self.get_object()
        group_id = request.data.get('group_id')
        user = request.user
        org = _get_clean_org(user)

        if not group_id:
            return Response({"error": "group_id majburiy maydon!"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            already_exists = StudentGroup.objects.filter(
                student=student,
                group_id=group_id,
                left_at__isnull=True
            ).exists()

            if already_exists:
                return Response({"message": "Talaba ushbu guruhda allaqachon bor!"}, status=status.HTTP_400_BAD_REQUEST)

            StudentGroup.objects.create(
                student=student,
                group_id=group_id,
                joined_at=timezone.now().date(),
                organization=org,
                created_by=user
            )
            return Response({"message": "Talaba guruhga muvaffaqiyatli qo'shildi"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# 2 ADASHIB O'CHIB KETGAN VA URLS.PY QIDIRAYOTGAN KLASS (XAVFSIZLASHTIRILDI)
class StudentGroupLeavesViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    # Agar seryalizatoringiz nomi boshqacha bo'lsa, o'zingiznikiga moslab qo'ying:
    # serializer_class = StudentGroupLeavesSerializer

    def get_queryset(self):
        org = _get_clean_org(self.request.user)
        # Agar modelingiz nomi xato bo'lsa, o'zingizning StudentGroupLeaves modeliga qarang
        return StudentGroupLeaves.objects.filter(organization=org).order_by('-created_at')

    def perform_create(self, serializer):
        org = _get_clean_org(self.request.user)
        leave = serializer.save(
            organization=org,
            branch=getattr(self.request.user, 'branch', None),
            created_by=self.request.user
        )
        _log_audit(self.request, AuditEntityType.STUDENT, leave.id, AuditAction.UPDATE,
                   new_data={"action": "Talaba guruhdan chiqdi/chetlashtirildi"})
class TalabalarMalumotView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        org = getattr(user, 'organization', None)
        if not org and hasattr(user, 'employee') and user.employee:
            org = getattr(user.employee, 'organization', None)

        students = Student.objects.filter(organization=org).select_related('balance_info').prefetch_related(
            Prefetch('student_groups', queryset=StudentGroup.objects.select_related('group').filter(left_at__isnull=True)),
            Prefetch('transactions', queryset=StudentTransaction.objects.order_by('-transaction_date'))
        )

        result = []
        for student in students:
            balans = float(student.balance_info.balance) if hasattr(student, 'balance_info') else 0
            guruhlar = [sg.group.name for sg in student.student_groups.all()]
            last_trans = student.transactions.first()

            result.append({
                "student_id": str(student.id),
                "student_ism": student.full_name,
                "student_telefon": student.phone_number,
                "guruhlar": ", ".join(guruhlar) if guruhlar else "Biriktirilmagan",
                "balans": balans,
                "izoh": last_trans.comment if last_trans else "",
            })
        return Response(result, status=200)


class StudentAddPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, student_id):
        try:
            amount_raw = request.data.get('amount')
            if not amount_raw:
                return Response({'error': "Summani kiriting"}, status=400)

            amount = Decimal(str(amount_raw))
            if amount <= 0:
                raise InvalidOperation

            user = request.user
            org = getattr(user, 'organization', None)
            if not org and hasattr(user, 'employee') and user.employee:
                org = getattr(user.employee, 'organization', None)

            from django.utils import timezone
            from datetime import timedelta
            bir_daqiqa_oldin = timezone.now() - timedelta(minutes=1)

            double_check = StudentTransaction.objects.filter(
                student_id=student_id,
                amount=amount,
                transaction_type='payment',
                organization=org,
                created_at__gte=bir_daqiqa_oldin
            ).exists()

            if double_check:
                return Response({'error': "Ketma-ket so'rov aniqlandi. 1 daqiqa kuting!"}, status=400)

            with transaction.atomic():
                student = get_object_or_404(Student.objects.select_for_update(), pk=student_id, organization=org)

                txn = StudentTransaction.objects.create(
                    student=student,
                    amount=amount,
                    transaction_type='payment',
                    payment_type=request.data.get('payment_type', 'cash'),
                    comment=request.data.get('comment', ''),
                    organization=org,
                    created_by=user
                )

                balance_obj, _ = StudentBalances.objects.get_or_create(
                    student=student,
                    defaults={'balance': Decimal('0'), 'organization': org}
                )
                old_balance = balance_obj.balance
                balance_obj.balance = old_balance + amount
                balance_obj.save()

            _log_audit(request, AuditEntityType.PAYMENT, txn.id, AuditAction.CREATE,
                       old_data={'balance': str(old_balance)},
                       new_data={'amount': str(amount), 'new_balance': str(balance_obj.balance)})

            return Response({'success': True, 'new_balance': str(balance_obj.balance)}, status=201)
        except InvalidOperation:
            return Response({'error': "Noto'g'ri summa"}, status=400)
        except Exception as e:
            return Response({'error': str(e)}, status=400)


class StudentLeaveFreezeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, action):
        student_id = request.data.get('student')
        user = request.user
        org = getattr(user, 'organization', None)
        if not org and hasattr(user, 'employee') and user.employee:
            org = getattr(user.employee, 'organization', None)

        student = get_object_or_404(Student, pk=student_id, organization=org)

        if action == 'leave':
            # 🟢 SIZDA SERIALIZER IMPORT BO'LMAGAN, SHU ERDA TO'G'RILANDI
            serializer = StudentGroupLeavesSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                leave = serializer.save(organization=org, created_by=user)

                sg = leave.student_group
                sg.left_at = leave.leave_date
                sg.save()

                if leave.refund_amount > 0:
                    with transaction.atomic():
                        bal, _ = StudentBalances.objects.get_or_create(student=student, defaults={'organization': org})
                        bal.balance += leave.refund_amount
                        bal.save()
                        StudentTransaction.objects.create(
                            student=student, amount=leave.refund_amount, transaction_type='refund',
                            payment_type='cash', comment="Guruhdan chiqish uchun qaytarildi",
                            organization=org, created_by=user
                        )
                _log_audit(request, AuditEntityType.STUDENT, student.id, AuditAction.UPDATE, new_data={"action": "Guruhdan chiqdi"})
                return Response({"message": "Talaba guruhdan chiqarildi"}, status=200)

        elif action == 'freeze':
            serializer = StudentFreezeSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save(organization=org, created_by=user)
                _log_audit(request, AuditEntityType.STUDENT, student.id, AuditAction.UPDATE, new_data={"action": "Muzlatildi"})
                return Response({"message": "Talaba muzlatildi"}, status=201)

        return Response(serializer.errors, status=400)


# QOLGAN BARCHA VIEWSETLAR UNIVERSALBASEVIEWSET GA O'TKAZILDI
class StudentPricingViewSet(UniversalBaseViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = StudentPricingSerializer
    queryset = StudentPricing.objects.all()


class StudentGroupViewSet(UniversalBaseViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = StudentGroupSerializer
    queryset = StudentGroup.objects.all()


class StudentTransactionViewSet(UniversalBaseViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = StudentTransactionSerializer
    queryset = StudentTransaction.objects.all()


class LeaveReasonViewSet(UniversalBaseViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = LeaveReasonSerializer
    queryset = LeaveReason.objects.all()


class StudentBalanceHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = StudentBalanceHistorySerializer

    def get_queryset(self):
        user = self.request.user
        org = getattr(user, 'organization', None)
        if not org and hasattr(user, 'employee') and user.employee:
            org = getattr(user.employee, 'organization', None)
        return StudentBalanceHistory.objects.filter(organization=org)


class StudentBalanceViewSet(UniversalBaseViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = StudentBalanceSerializer
    queryset = StudentBalances.objects.all()