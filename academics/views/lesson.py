from datetime import date
from decimal import Decimal
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# 1. Modellar importi (Har biri o'z faylidan)
from academics.models.lesson import (
    LessonSchedule, Attendance, Exams, ExamResults, OnlineLesson,LessonTime
)
from academics.models.group import Group  # Group bu yerda!
from academics.models.student import (
    StudentGroup, StudentBalances, StudentBalanceHistory
)

# 2. Serializerlar importi
# Strukturangizga ko'ra academics/serializers/lesson.py faylidan:
from academics.serializers.lesson import (
    LessonScheduleSerializer,
    LessonScheduleListSerializer,
    AttendenceSerializer,
    ExamSerializer,
    ExamResultSerializer,
    OnlineLessonSerializer,LessonTimeSerializer
)

# 3. Audit va boshqalar
from audit.models import AuditLog, AuditAction, AuditEntityType

# --- Yordamchi Audit Funksiyasi ---
def _log_audit(request, entity_type, entity_id, action, old_data=None, new_data=None):
    employee = getattr(request.user, 'employee', None)
    role = getattr(employee, 'position', "Admin") if employee else "System"
    AuditLog.objects.create(
        organization=request.user.organization,
        branch=getattr(request.user, 'branch', None),
        created_by=request.user,
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        old_data=old_data,
        new_data=new_data,
        performed_by_role=f"{role} ({request.user.full_name})"
    )
class LessonTimeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = LessonTimeSerializer

    def get_queryset(self):
        return LessonTime.objects.filter(organization=self.request.user.organization)

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization)
class ExamResultViewSet(viewsets.ReadOnlyModelViewSet): # Faqat ko'rish uchun, chunki GradingView orqali kiritiladi
    permission_classes = [IsAuthenticated]
    serializer_class = ExamResultSerializer

    def get_queryset(self):
        return ExamResults.objects.filter(
            organization=self.request.user.organization
        ).select_related('exam', 'student')
# ==========================================
# 1. DARS JADVALLARI
# ==========================================
class LessonScheduleViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Faqat o'z tashkilotidagi jadvallar
        return LessonSchedule.objects.filter(organization=self.request.user.organization).select_related('group')

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return LessonScheduleListSerializer
        return LessonScheduleSerializer

    def perform_create(self, serializer):
        schedule = serializer.save(
            organization=self.request.user.organization,
            branch=getattr(self.request.user, 'branch', None),
            created_by=self.request.user
        )
        _log_audit(self.request, AuditEntityType.OTHER, schedule.id, AuditAction.CREATE,
                   new_data={"day_type": schedule.day_type, "time": f"{schedule.start_time}-{schedule.end_time}"})


# ==========================================
# 2. DAVOMAT VA PUL YECHISH MANTIQI
# ==========================================
class GroupAttendanceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, group_id):
        # Tashkilot tekshiruvi bilan guruhni olish
        group = get_object_or_404(Group, pk=group_id, organization=request.user.organization)
        lesson_date = request.GET.get('date', date.today().isoformat())

        student_groups = StudentGroup.objects.filter(group=group, left_at__isnull=True)
        attendances = Attendance.objects.filter(student_group__in=student_groups, lesson_date=lesson_date)

        data = []
        for sg in student_groups:
            att = attendances.filter(student_group=sg).first()
            data.append({
                'student_group_id': str(sg.id),
                'student_name': sg.student.full_name,
                'is_present': att.is_present if att else None
            })
        return Response({'success': True, 'date': str(lesson_date), 'results': data})

    @transaction.atomic
    def post(self, request, group_id):
        group = get_object_or_404(Group, pk=group_id, organization=request.user.organization)
        student_group_id = request.data.get('student_group')
        is_present = request.data.get('is_present', False)
        lesson_date = request.data.get('lesson_date', date.today())

        student_group = get_object_or_404(StudentGroup, pk=student_group_id, group=group)

        # Allaqachon davomat qo'yilgan bo'lsa yangilaymiz (yoki xato beramiz)
        attendance, created = Attendance.objects.update_or_create(
            student_group=student_group,
            lesson_date=lesson_date,
            defaults={'is_present': is_present, 'marked_by': request.user}
        )

        # BIZNES MANTIQ: Agar bugun kelgan bo'lsa va bu birinchi marta kiritilayotgan bo'lsa, pul yechamiz
        deducted_amount = 0
        if is_present and created:
            student = student_group.student
            course = group.course
            if course:
                # Bir dars narxini hisoblash
                lessons_count = Decimal(course.lessons_per_month) if course.lessons_per_month else Decimal(12)
                one_lesson_price = Decimal(course.monthly_price) / lessons_count

                # Balansdan ayirish
                balance_obj, _ = StudentBalances.objects.get_or_create(student=student, defaults={'balance': Decimal('0')})
                balance_obj.balance -= one_lesson_price
                balance_obj.save()
                deducted_amount = float(one_lesson_price)

                # Tarixga yozish
                StudentBalanceHistory.objects.create(
                    student=student, amount=-one_lesson_price,
                    base_price=course.monthly_price, applied_price=one_lesson_price
                )

        # ── Audit Log ──
        _log_audit(self.request, AuditEntityType.OTHER, attendance.id, AuditAction.CREATE, new_data={
            "student_id": str(student_group.student.id),
            "is_present": is_present,
            "deducted_amount": deducted_amount
        })

        return Response({'success': True, 'message': "Davomat saqlandi", 'deducted': deducted_amount}, status=201)



# 3. IMTIHONLAR

class ExamsViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ExamSerializer

    def get_queryset(self):
        employee = getattr(self.request.user, 'employee', None)
        if not employee:
            return Exams.objects.none()
        return Exams.objects.filter(organization=employee.organization).order_by('-exam_date')

    def perform_create(self, serializer):
        # 1. Employee ni olamiz
        employee = getattr(self.request.user, 'employee', None)
        # 2. Tekshiramiz: Agar employee bo'lmasa, 'AttributeError' chiqishiga yo'l qo'ymaymiz
        if employee is None:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"detail": "Siz tizimda xodim sifatida ro'yxatdan o'tmagansiz!"})
        # 3. Faqat employee borligiga ishonganimizdan keyin organization ni olamiz
        serializer.save(
            organization=employee.organization,
            created_by=employee
        )
        _log_audit(self.request, AuditEntityType.OTHER, exam.id, AuditAction.CREATE, new_data={"title": exam.title})


class ExamGradingView(APIView):
    """ Imtihon baholarini kiritish (unique_together qoidasi bilan) """
    permission_classes = [IsAuthenticated]
    def post(self, request):
        exam_id = request.data.get('exam')
        student_id = request.data.get('student')
        score = request.data.get('score')
        exam = get_object_or_404(Exams, pk=exam_id, organization=request.user.organization)
        # Bahoni yaratish yoki yangilash
        result, created = ExamResults.objects.update_or_create(
            exam=exam, student_id=student_id,
            defaults={'score': score, 'comment': request.data.get('comment', '')}
        )
        _log_audit(self.request, AuditEntityType.OTHER, result.id, AuditAction.UPDATE if not created else AuditAction.CREATE,
                   new_data={"student": str(student_id), "score": str(score)})
        return Response({'success': True, 'message': 'Baho saqlandi', 'score': result.score}, status=200)



# 4. ONLAYN DARSLAR
class OnlineLessonViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = OnlineLessonSerializer

    def get_queryset(self):
        return OnlineLesson.objects.filter(organization=self.request.user.organization).order_by('order')
    def perform_create(self, serializer):
        lesson = serializer.save(
            organization=self.request.user.organization,
            created_by=self.request.user
        )
        _log_audit(self.request, AuditEntityType.OTHER, lesson.id, AuditAction.CREATE, new_data={"title": lesson.title})

class PublishLessonView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, lesson_id):
        lesson = get_object_or_404(OnlineLesson, pk=lesson_id, organization=request.user.organization)
        lesson.is_published = True
        lesson.save()
        _log_audit(self.request, AuditEntityType.OTHER, lesson.id, AuditAction.UPDATE, new_data={"is_published": True})
        return Response({'success': True, 'message': "Dars o'quvchilarga ko'rinadigan bo'ldi!"})



