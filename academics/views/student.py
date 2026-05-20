from decimal import Decimal, InvalidOperation
from django.db import transaction
from django.db.models import Prefetch, F
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action
from academics.models import (
    Student, StudentGroup, StudentBalances, StudentTransaction, StudentGroupLeaves, StudentFreezes,StudentPricing,LeaveReason,StudentBalanceHistory
)
from academics.serializers.student import (
    StudentSerializer, StudentTransactionSerializer, StudentFreezeSerializer,StudentPricingSerializer,StudentGroupSerializer,LeaveReasonSerializer,StudentBalanceHistorySerializer,StudentBalanceSerializer,StudentGroupLeavesSerializer
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


class StudentGroupLeavesViewSet(viewsets.ModelViewSet):
    queryset = StudentGroupLeaves.objects.all().order_by('-leave_date')
    serializer_class = StudentGroupLeavesSerializer


class StudentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = StudentSerializer

    def get_queryset(self):
        # Tashkilot himoya qatlami
        print("organization -> ", self.request.user.organization)
        return Student.objects.filter(
            organization=self.request.user.organization
        ).select_related('balance_info').order_by('-created_at')

    def perform_create(self, serializer):
        print("organization -> ", self.request.user.organization)
        organization = self.request.user.organization
        print("organization ->", organization)
        # =================================================================
        # 1. SAAS TARIF LIMITINI TEKSHIRISH
        # =================================================================
        # Hozirgi aktiv o'quvchilar sonini hisoblaymiz
        current_count = Student.objects.filter(
            organization=organization,
            status='active'  # is_active o'rniga status='active' ishlatamiz
        ).count()

        # Limitdan oshib ketmaganligini tekshiramiz
        # if not organization.has_student_capacity(current_count):
        #     raise ValidationError({
        #         "limit_error": "Tarif limitingiz tugadi! O'quvchilar soni tarifda belgilanganidan oshib ketdi. Iltimos, tarifingizni yangilang."
        #     })

        # =================================================================
        # 2. ASOSIY YARATISH JARAYONI (MOLIYA VA AUDIT BILAN)
        # =================================================================
        with transaction.atomic():
            # Agar hammasi joyida bo'lsa, saqlaymiz
            student = serializer.save(
                organization=organization,
                branch=getattr(self.request.user, 'branch', None),
                created_by=self.request.user
            )

            # Yangi talabaga avtomatik 0 so'm balans ochamiz
            StudentBalances.objects.create(
                student=student,
                organization=organization,
                branch=getattr(self.request.user, 'branch', None)
            )

        # Audit Log yozib qoldiramiz
        self._log_audit(
            entity_type=AuditEntityType.STUDENT,
            entity_id=student.id,
            action=AuditAction.CREATE,
            new_data={"name": student.full_name, "phone": student.phone_number}
        )

    # (Yordamchi metod Audit uchun)
    def _log_audit(self, entity_type, entity_id, action, old_data=None, new_data=None):
        AuditLog.objects.create(
            organization=self.request.user.organization,
            branch=getattr(self.request.user, 'branch', None),
            created_by=self.request.user,
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            old_data=old_data,
            new_data=new_data
        )


    # 2. ALOHIDA METOD SIFATIDA CHIQARAMIZ
    @action(detail=True, methods=['post'], url_path='add-to-group')
    def add_to_group(self, request, pk=None):
        student = self.get_object()
        group_id = request.data.get('group_id')

        if not group_id:
            return Response({"error": "group_id majburiy maydon!"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 🔥 XATO SHU YERDA EDI: student.groups.add(group_id) o'rniga
            # StudentGroup modeli orqali yangi bog'liqlik (yozuv) yaratamiz:

            # Agar talaba allaqachon shu guruhda faol bo'lsa, qayta qo'shmaymiz
            already_exists = StudentGroup.objects.filter(
                student=student,
                group_id=group_id,
                left_at__isnull=True  # Guruhdan chiqib ketmagan bo'lsa
            ).exists()

            if already_exists:
                return Response({"message": "Talaba ushbu guruhda allaqachon bor!"}, status=status.HTTP_400_BAD_REQUEST)

            # Guruhga yangi biriktirish yaratamiz
            StudentGroup.objects.create(
                student=student,
                group_id=group_id,
                organization=request.user.organization,
                created_by=request.user
            )

            return Response({"message": "Talaba guruhga muvaffaqiyatli qo'shildi"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
class TalabalarMalumotView(APIView):
    """ Barcha talabalar haqida to'liq hisobot (N+1 muammosisiz optimallashtirilgan) """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Optimallashtirilgan so'rov (Database ga 1000 marta emas, 3 marta murojaat qiladi)
        students = Student.objects.filter(organization=request.user.organization).select_related(
            'balance_info').prefetch_related(
            Prefetch('student_groups',
                     queryset=StudentGroup.objects.select_related('group').filter(left_at__isnull=True)),
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
    """ Talabadan to'lov qabul qilish va balansni oshirish """
    permission_classes = [IsAuthenticated]

    def post(self, request, student_id):
        try:
            # Kelayotgan summani tekshiramiz
            amount_raw = request.data.get('amount')
            if not amount_raw:
                return Response({'error': "Summani kiriting"}, status=400)

            amount = Decimal(str(amount_raw))
            if amount <= 0:
                raise InvalidOperation

            # 🔥 DUBLE TO'LOVNING OLDINI OLISH (IDEMPOTENCY)
            from django.utils import timezone
            from datetime import timedelta

            # Oxirgi 1 daqiqa (60 soniya) vaqt oralig'ini olamiz
            bir_daqiqa_oldin = timezone.now() - timedelta(minutes=1)

            # Bazada aynan shu talabaga, aynan shu summada, oxirgi 1 daqiqada to'lov yaratilganmi?
            double_check = StudentTransaction.objects.filter(
                student_id=student_id,
                amount=amount,
                transaction_type='payment',
                organization=request.user.organization,
                created_at__gte=bir_daqiqa_oldin  # Agar modelingizda 'created_at' bo'lsa. (Agar yo'q bo'lsa 'transaction_date__gte' qiling)
            ).exists()

            if double_check:
                return Response({
                    'error': "Tizim ketma-ket (dublikat) so'rovni aniqladi! Iltimos, 1 daqiqa kuting yoki tugmani qayta bosmang."
                }, status=400)

            # =================================================================
            # ASOSIY BAZAGA YOZISH JARAYONI
            # =================================================================
            with transaction.atomic():
                # select_for_update() balansni parallel so'rovlarda noto'g'ri hisoblanishidan himoya qiladi
                student = get_object_or_404(
                    Student.objects.select_for_update(),
                    pk=student_id,
                    organization=request.user.organization
                )

                # Tranzaksiyani yaratish
                txn = StudentTransaction.objects.create(
                    student=student,
                    amount=amount,
                    transaction_type='payment',
                    payment_type=request.data.get('payment_type', 'cash'),
                    comment=request.data.get('comment', ''),
                    organization=request.user.organization,
                    created_by=request.user
                )

                # Balansni yangilash
                balance_obj, _ = StudentBalances.objects.get_or_create(
                    student=student,
                    defaults={'balance': Decimal('0'), 'organization': request.user.organization}
                )
                old_balance = balance_obj.balance
                balance_obj.balance = old_balance + amount
                balance_obj.save()

            # Audit Log
            _log_audit(request, AuditEntityType.PAYMENT, txn.id, AuditAction.CREATE,
                       old_data={'balance': str(old_balance)},
                       new_data={'amount': str(amount), 'new_balance': str(balance_obj.balance)})

            return Response(
                {'success': True, 'new_balance': str(balance_obj.balance), 'message': "To'lov qabul qilindi."},
                status=201)

        except InvalidOperation:
            return Response({'error': "Noto'g'ri summa kiritildi"}, status=400)
        except Exception as e:
            return Response({'error': str(e)}, status=400)
class StudentLeaveFreezeView(APIView):
    """ Talabani guruhdan chiqarish yoki muzlatish """
    permission_classes = [IsAuthenticated]

    def post(self, request, action):
        student_id = request.data.get('student')
        student = get_object_or_404(Student, pk=student_id, organization=request.user.organization)

        if action == 'leave':
            serializer = StudentLeavesSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                leave = serializer.save(organization=request.user.organization, created_by=request.user)

                # Guruhdan chiqish vaqtini belgilaymiz
                sg = leave.student_group
                sg.left_at = leave.leave_date
                sg.save()

                # Agar pul qaytarilishi kerak bo'lsa
                if leave.refund_amount > 0:
                    with transaction.atomic():
                        bal, _ = StudentBalances.objects.get_or_create(student=student)
                        bal.balance += leave.refund_amount
                        bal.save()
                        StudentTransaction.objects.create(
                            student=student, amount=leave.refund_amount, transaction_type='refund',
                            payment_type='cash', comment="Guruhdan chiqish uchun qaytarildi", created_by=request.user
                        )
                _log_audit(request, AuditEntityType.STUDENT, student.id, AuditAction.UPDATE,
                           new_data={"action": "Guruhdan chiqdi"})
                return Response({"message": "Talaba guruhdan chiqarildi"}, status=200)

        elif action == 'freeze':
            serializer = StudentFreezeSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save(organization=request.user.organization, created_by=request.user)
                _log_audit(request, AuditEntityType.STUDENT, student.id, AuditAction.UPDATE,
                           new_data={"action": "Muzlatildi"})
                return Response({"message": "Talaba muzlatildi"}, status=201)

        return Response(serializer.errors, status=400)


# 1. Individual narxlar
class StudentPricingViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = StudentPricingSerializer
    def get_queryset(self):
        return StudentPricing.objects.filter(organization=self.request.user.organization)
    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization, created_by=self.request.user)

# 2. Guruhga biriktirish (StudentGroup)
class StudentGroupViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = StudentGroupSerializer
    def get_queryset(self):
        return StudentGroup.objects.filter(organization=self.request.user.organization)
    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization, created_by=self.request.user)

# 3. Tranzaksiyalar tarixi (Faqat ko'rish va o'chirish/tahrirlash uchun)
class StudentTransactionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = StudentTransactionSerializer
    def get_queryset(self):
        return StudentTransaction.objects.filter(organization=self.request.user.organization)

# 4. Ketish sabablari (Lug'at)
class LeaveReasonViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = LeaveReasonSerializer
    def get_queryset(self):
        return LeaveReason.objects.filter(organization=self.request.user.organization)
    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization, created_by=self.request.user)

# 5. Balans tarixi
class StudentBalanceHistoryViewSet(viewsets.ReadOnlyModelViewSet): # Faqat o'qish uchun
    permission_classes = [IsAuthenticated]
    serializer_class = StudentBalanceHistorySerializer
    def get_queryset(self):
        return StudentBalanceHistory.objects.filter(organization=self.request.user.organization)

class StudentBalanceViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = StudentBalanceSerializer

    def get_queryset(self):
        # Faqat o'z tashkilotining balanslarini ko'radi
        return StudentBalances.objects.filter(
            organization=self.request.user.organization
        ).select_related('student').order_by('-balance')

    def perform_create(self, serializer):
        # Balans yaratilayotganda avtomatik tashkilot va filialni biriktiramiz
        serializer.save(
            organization=self.request.user.organization,
            branch=getattr(self.request.user, 'branch', None)
        )