from datetime import date
from decimal import Decimal
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.apps import apps
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from academics.models.lesson import LessonSchedule, Attendance, Exams, ExamResults, OnlineLesson, LessonTime
from academics.models.group import Group
from academics.models.student import StudentGroup, StudentBalances, StudentBalanceHistory
from academics.serializers.lesson import (
    LessonScheduleSerializer, LessonScheduleListSerializer,
    AttendenceSerializer, ExamSerializer, ExamResultSerializer,
    OnlineLessonSerializer, LessonTimeSerializer
)
from audit.models import AuditLog, AuditAction, AuditEntityType

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
    org = _get_clean_org(request.user)
    employee = getattr(request.user, 'employee', None)
    role = getattr(employee, 'position', "Admin") if employee else "System"
    AuditLog.objects.create(
        organization=org,
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
        org = _get_clean_org(self.request.user)
        return LessonTime.objects.filter(organization=org)

    def perform_create(self, serializer):
        serializer.save(organization=_get_clean_org(self.request.user))

class ExamResultViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ExamResultSerializer

    def get_queryset(self):
        org = _get_clean_org(self.request.user)
        return ExamResults.objects.filter(organization=org).select_related('exam', 'student')

class LessonScheduleViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        org = _get_clean_org(self.request.user)
        return LessonSchedule.objects.filter(organization=org).select_related('group')

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return LessonScheduleListSerializer
        return LessonScheduleSerializer

    def perform_create(self, serializer):
        org = _get_clean_org(self.request.user)
        schedule = serializer.save(
            organization=org,
            branch=getattr(self.request.user, 'branch', None),
            created_by=self.request.user
        )
        _log_audit(self.request, AuditEntityType.OTHER, schedule.id, AuditAction.CREATE,
                   new_data={"day_type": schedule.day_type, "time": f"{schedule.start_time}-{schedule.end_time}"})

class GroupAttendanceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, group_id):
        org = _get_clean_org(request.user)
        group = get_object_or_404(Group, pk=group_id, organization=org)
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
        org = _get_clean_org(request.user)
        group = get_object_or_404(Group, pk=group_id, organization=org)
        student_group_id = request.data.get('student_group')
        is_present = request.data.get('is_present', False)
        lesson_date = request.data.get('lesson_date', date.today())

        student_group = get_object_or_404(StudentGroup, pk=student_group_id, group=group)

        attendance, created = Attendance.objects.update_or_create(
            student_group=student_group,
            lesson_date=lesson_date,
            defaults={
                'is_present': is_present,
                'organization': org,
                'created_by': request.user
            }
        )

        deducted_amount = 0
        if is_present and created:
            student = student_group.student
            course = group.course
            if course:
                lessons_count = Decimal(course.lessons_per_month) if course.lessons_per_month else Decimal(12)
                one_lesson_price = Decimal(course.monthly_price) / lessons_count

                balance_obj, _ = StudentBalances.objects.get_or_create(student=student, defaults={'balance': Decimal('0')})
                balance_obj.balance -= one_lesson_price
                balance_obj.save()
                deducted_amount = float(one_lesson_price)
                StudentBalanceHistory.objects.create(
                    student=student,
                    amount=-one_lesson_price,
                    base_price=course.monthly_price,
                    applied_price=one_lesson_price,
                    organization=org
                )

        _log_audit(request, AuditEntityType.OTHER, attendance.id, AuditAction.CREATE, new_data={
            "student_id": str(student_group.student.id),
            "is_present": is_present,
            "deducted_amount": deducted_amount
        })
        return Response({'success': True, 'message': "Davomat saqlandi", 'deducted': deducted_amount}, status=201)

    @transaction.atomic
    def patch(self, request, group_id):
        org = _get_clean_org(request.user)
        group = get_object_or_404(Group, pk=group_id, organization=org)
        lesson_date = request.data.get('lesson_date', date.today())
        students_data = request.data.get('students', [])

        if not students_data:
            return Response({"error": "Talabalar davomat ro'yxati (students) yuborilmadi!"}, status=400)

        course = group.course
        one_lesson_price = Decimal('0')
        if course:
            lessons_count = Decimal(course.lessons_per_month) if course.lessons_per_month else Decimal(12)
            one_lesson_price = Decimal(course.monthly_price) / lessons_count

        for item in students_data:
            sg_id = item.get('student_group_id')
            new_is_present = item.get('is_present', False)

            student_group = get_object_or_404(StudentGroup, pk=sg_id, group=group)
            student = student_group.student
            balance_obj, _ = StudentBalances.objects.get_or_create(student=student, defaults={'balance': Decimal('0')})

            old_attendance = Attendance.objects.filter(student_group=student_group, lesson_date=lesson_date).first()
            old_is_present = old_attendance.is_present if old_attendance else None

            Attendance.objects.update_or_create(
                student_group=student_group,
                lesson_date=lesson_date,
                defaults={'is_present': new_is_present, 'organization': org, 'created_by': request.user}
            )

            if not old_is_present and new_is_present:
                balance_obj.balance -= one_lesson_price
                balance_obj.save()
                StudentBalanceHistory.objects.create(
                    student=student, amount=-one_lesson_price,
                    base_price=course.monthly_price, applied_price=one_lesson_price,
                    comment="Davomat tahrirlangani sababli pul yechildi", organization=org
                )
            elif old_is_present and not new_is_present:
                balance_obj.balance += one_lesson_price
                balance_obj.save()
                StudentBalanceHistory.objects.create(
                    student=student, amount=one_lesson_price,
                    base_price=course.monthly_price, applied_price=one_lesson_price,
                    comment="Davomat xatosi tuzatilgani sababli pul qaytarildi", organization=org
                )
        _log_audit(request, AuditEntityType.OTHER, group.id, AuditAction.UPDATE,
                   new_data={"group": group.name, "date": str(lesson_date), "action": "Davomat tahrirlandi"})
        return Response({'success': True, 'message': "Davomat muvaffaqiyatli yangilandi"})

    @transaction.atomic
    def delete(self, request, group_id):
        org = _get_clean_org(request.user)
        group = get_object_or_404(Group, pk=group_id, organization=org)
        lesson_date = request.query_params.get('date') or request.data.get('date')

        if not lesson_date:
            return Response({"error": "Sana (date) parametri yuborilmadi!"}, status=400)

        student_groups = StudentGroup.objects.filter(group=group)
        attendances = Attendance.objects.filter(student_group__in=student_groups, lesson_date=lesson_date)

        if not attendances.exists():
            return Response({"error": "Ushbu sana uchun davomat topilmadi"}, status=404)

        course = group.course
        one_lesson_price = Decimal('0')
        if course:
            lessons_count = Decimal(course.lessons_per_month) if course.lessons_per_month else Decimal(12)
            one_lesson_price = Decimal(course.monthly_price) / lessons_count

        for att in attendances:
            if att.is_present:
                student = att.student_group.student
                balance_obj = StudentBalances.objects.filter(student=student).first()
                if balance_obj:
                    balance_obj.balance += one_lesson_price
                    balance_obj.save()
                    StudentBalanceHistory.objects.create(
                        student=student, amount=one_lesson_price,
                        base_price=course.monthly_price, applied_price=one_lesson_price,
                        comment="Davomat o'chirilgani sababli pul qaytarildi", organization=org
                    )
        attendances.delete()
        _log_audit(request, AuditEntityType.OTHER, group.id, AuditAction.DELETE,
                   old_data={"group": group.name, "date": str(lesson_date), "action": "Davomat o'chirildi"})
        return Response({'success': True, 'message': "Davomat o'chirildi va pullar talabalarga qaytarildi"})

class ExamsViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ExamSerializer

    def get_queryset(self):
        org = _get_clean_org(self.request.user)
        if not org:
            return Exams.objects.none()
        return Exams.objects.filter(organization=org).order_by('-exam_date')

    def perform_create(self, serializer):
        org = _get_clean_org(self.request.user)
        if not org:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"detail": "Siz biror bir tashkilotga biriktirilmagansiz!"})
        exam = serializer.save(organization=org, created_by=self.request.user)
        _log_audit(self.request, AuditEntityType.OTHER, exam.id, AuditAction.CREATE, new_data={"title": exam.title})

class ExamGradingView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        org = _get_clean_org(request.user)
        exam_id = request.data.get('exam')
        student_id = request.data.get('student')
        score = request.data.get('score')
        exam = get_object_or_404(Exams, pk=exam_id, organization=org)
        result, created = ExamResults.objects.update_or_create(
            exam=exam, student_id=student_id,
            defaults={'score': score, 'comment': request.data.get('comment', '')}
        )
        _log_audit(self.request, AuditEntityType.OTHER, result.id, AuditAction.UPDATE if not created else AuditAction.CREATE,
                   new_data={"student": str(student_id), "score": str(score)})
        return Response({'success': True, 'message': 'Baho saqlandi', 'score': result.score}, status=200)

class OnlineLessonViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = OnlineLessonSerializer

    def get_queryset(self):
        org = _get_clean_org(self.request.user)
        return OnlineLesson.objects.filter(organization=org).order_by('order')

    def perform_create(self, serializer):
        org = _get_clean_org(self.request.user)
        lesson = serializer.save(organization=org, created_by=self.request.user)
        _log_audit(self.request, AuditEntityType.OTHER, lesson.id, AuditAction.CREATE, new_data={"title": lesson.title})

class PublishLessonView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, lesson_id):
        org = _get_clean_org(request.user)
        lesson = get_object_or_404(OnlineLesson, pk=lesson_id, organization=org)
        lesson.is_published = True
        lesson.save()
        _log_audit(self.request, AuditEntityType.OTHER, lesson.id, AuditAction.UPDATE, new_data={"is_published": True})
        return Response({'success': True, 'message': "Dars o'quvchilarga ko'rinadigan bo'ldi!"})