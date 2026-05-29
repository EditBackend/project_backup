from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q
from django.db import transaction
from django.apps import apps

from academics.models import Group, Course, Room, GroupTeacher
from academics.serializers.groups import (
    GroupListSerializer, GroupDetailSerializer, GroupWriteSerializer,
    RoomSerializer, CourseMinimalSerializer, GroupTeacherSerializer
)
from audit.models import AuditLog, AuditAction, AuditEntityType


# 1. Tashkilotni har qanday foydalanuvchidan (Superadmin, Employee yoki Employee Profile) xavfsiz aniqlash funksiyasi
def _get_clean_org(user):
    if hasattr(user, 'organization') and user.organization:
        return user.organization
    if hasattr(user, 'employee') and user.employee and getattr(user.employee, 'organization', None):
        return user.employee.organization
    if hasattr(user, 'employee_profile') and user.employee_profile and getattr(user.employee_profile, 'organization',
                                                                               None):
        return user.employee_profile.organization
    try:
        Organization = apps.get_model('organizations', 'Organization')
        return Organization.objects.first()
    except Exception:
        return None


# 2. Universal Audit funksiyasi
def _log_audit(request, entity_type, entity_id, action, old_data=None, new_data=None):
    try:
        user = request.user
        org = _get_clean_org(user)

        employee = getattr(user, 'employee', None) or getattr(user, 'employee_profile', None)
        role = getattr(employee, 'position', "Admin") if employee else "System"

        AuditLog.objects.create(
            organization=org,
            branch=getattr(user, 'branch', None),
            created_by=user,
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            old_data=old_data,
            new_data=new_data,
            performed_by_role=f"{role} ({getattr(user, 'full_name', user.username)})"
        )
    except Exception as e:
        print(f"Audit yozishda xatolik: {e}")


# 3. GURUH O'QITUVCHILARI VIEWSETI
class GroupTeacherViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = GroupTeacherSerializer

    def get_queryset(self):
        org = _get_clean_org(self.request.user)
        if not org:
            return GroupTeacher.objects.none()
        return GroupTeacher.objects.filter(organization=org).select_related('group', 'teacher__user')

    def perform_create(self, serializer):
        org = _get_clean_org(self.request.user)
        serializer.save(
            organization=org,
            created_by=self.request.user
        )


# 4. GURUHLAR VIEWSETI
class GroupViewSet(viewsets.ModelViewSet):
    """
    Guruhlar uchun to'liq CRUD, filtrlar va Audit Log qatlami.
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status', 'course', 'room']
    search_fields = ['name']

    def get_queryset(self):
        user = self.request.user
        org = _get_clean_org(user)

        if user.is_superuser or not org:
            return Group.objects.all().select_related('course', 'room')

        return Group.objects.filter(organization=org).select_related('course', 'room').annotate(
            student_count=Count('group_students', filter=Q(group_students__left_at__isnull=True), distinct=True),
            teacher_count=Count('group_teachers', filter=Q(group_teachers__end_date__isnull=True), distinct=True)
        ).order_by('-created_at')

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return GroupWriteSerializer
        if self.action == 'list':
            return GroupListSerializer
        return GroupDetailSerializer

    def perform_create(self, serializer):
        org = _get_clean_org(self.request.user)
        group = serializer.save(
            organization=org,
            branch=getattr(self.request.user, 'branch', None),
            created_by=self.request.user
        )
        _log_audit(self.request, AuditEntityType.GROUP, group.id, AuditAction.CREATE,
                   old_data=None, new_data={"name": group.name, "status": group.status})

    def perform_update(self, serializer):
        old_instance = self.get_object()
        old_data = {
            "name": old_instance.name,
            "status": old_instance.status,
            "room": old_instance.room.name if old_instance.room else None
        }

        group = serializer.save()

        new_data = {"name": group.name, "status": group.status, "room": group.room.name if group.room else None}
        _log_audit(self.request, AuditEntityType.GROUP, group.id, AuditAction.UPDATE,
                   old_data=old_data, new_data=new_data)

    def perform_destroy(self, instance):
        _log_audit(self.request, AuditEntityType.GROUP, instance.id, AuditAction.DELETE,
                   old_data={"name": instance.name, "status": instance.status}, new_data=None)
        instance.delete()

    # Indentation xatosi to'g'rilandi: metod perform_destroy ichidan tashqariga chiqarildi
    @action(detail=True, methods=['patch', 'delete'], url_path='attendences')
    def manage_group_attendance(self, request, pk=None):
        """
        Guruh ID si orqali shu guruhning davomatini tahrirlash (PATCH) yoki o'chirish (DELETE)
        """
        try:
            from apps.academics.models import Attendance
        except ImportError:
            try:
                from academics.models import Attendance
            except ImportError:
                return Response({"error": "Attendance modeli topilmadi!"}, status=500)

        group = self.get_object()
        date = request.query_params.get('date') or request.data.get('date')

        if not date:
            return Response(
                {"error": "Sana (date) yuborilishi shart! Masalan: ?date=2026-05-20"},
                status=status.HTTP_400_BAD_REQUEST
            )

        attendance_records = Attendance.objects.filter(group=group, date=date)

        if not attendance_records.exists():
            return Response(
                {"error": "Ushbu guruh va sana uchun hech qanday davomat topilmadi!"},
                status=status.HTTP_404_NOT_FOUND
            )

        if request.method == 'DELETE':
            count = attendance_records.count()
            attendance_records.delete()

            _log_audit(request, AuditEntityType.ATTENDANCE, group.id, AuditAction.DELETE,
                       old_data={"group": group.name, "date": str(date), "deleted_count": count})

            return Response({"message": "Davomat muvaffaqiyatli o'chirildi"}, status=status.HTTP_200_OK)

        elif request.method == 'PATCH':
            students_data = request.data.get('students', [])

            if not students_data:
                return Response({"error": "Yangilanadigan talabalar ro'yxati (students) yuborilmadi!"}, status=400)

            with transaction.atomic():
                for item in students_data:
                    attendance_records.filter(
                        student_id=item.get('student_id')
                    ).update(
                        status=item.get('status'),
                        updated_by=request.user
                    )

            _log_audit(request, AuditEntityType.ATTENDANCE, group.id, AuditAction.UPDATE,
                       new_data={"group": group.name, "date": str(date), "action": "Davomat tahrirlandi"})

            return Response({"message": "Davomat muvaffaqiyatli yangilandi"}, status=status.HTTP_200_OK)


# 5. XONALAR VIEWSETI (XAVFSIZ QILINDI)
class RoomViewSet(viewsets.ModelViewSet):
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        org = _get_clean_org(self.request.user)
        if not org:
            return Room.objects.none()
        return Room.objects.filter(organization=org)

    def perform_create(self, serializer):
        org = _get_clean_org(self.request.user)
        if org:
            serializer.save(
                organization=org,
                created_by=self.request.user
            )
        else:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"detail": "Siz hech qaysi tashkilotga biriktirilmagansiz!"})


# 6. KURSLAR VIEWSETI (XAVFSIZ QILINDI)
class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseMinimalSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        org = _get_clean_org(self.request.user)
        if not org:
            return Course.objects.none()
        return Course.objects.filter(organization=org)

    def perform_create(self, serializer):
        org = _get_clean_org(self.request.user)
        if org:
            serializer.save(
                organization=org,
                created_by=self.request.user
            )
        else:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"detail": "Sizda tashkilot aniqlanmadi, kurs yarata olmaysiz!"})