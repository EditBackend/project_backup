from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q
from academics.models import Group, Course, Room,GroupTeacher
from academics.serializers.groups import (
    GroupListSerializer, GroupDetailSerializer, GroupWriteSerializer,
    RoomSerializer, CourseMinimalSerializer,GroupTeacherSerializer
)
from audit.models import AuditLog, AuditAction, AuditEntityType


# Yordamchi Audit funksiyasi
def _log_audit(request, entity_type, entity_id, action, old_data=None, new_data=None):
    try:
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
    except Exception as e:
        print(f"Audit yozishda xatolik: {e}")

class GroupTeacherViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = GroupTeacherSerializer

    def get_queryset(self):
        return GroupTeacher.objects.filter(
            organization=self.request.user.organization
        ).select_related('group', 'teacher__user')

    def perform_create(self, serializer):
        serializer.save(
            organization=self.request.user.organization,
            created_by=self.request.user
        )
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

        # User yoki Employee_profile orqali org'ni topish
        org = getattr(user, 'organization', None) or getattr(user, 'employee_profile', user).organization

        # Agar baribir topilmasa (masalan superuser bo'lsa)
        if not org:
            return Group.objects.all() # Superadmin hamma narsani ko'rsin

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

    # POST (Yaratish)
    def perform_create(self, serializer):
        # Frontenddan kutmasdan org va userni o'zimiz beramiz
        group = serializer.save(
            organization=self.request.user.organization,
            branch=getattr(self.request.user, 'branch', None),
            created_by=self.request.user
        )
        # ── Audit Log ──
        _log_audit(self.request, AuditEntityType.GROUP, group.id, AuditAction.CREATE,
                   old_data=None, new_data={"name": group.name, "status": group.status})

    # PUT/PATCH (Tahrirlash)
    def perform_update(self, serializer):
        # Eski ma'lumotlarni o'zgarishdan oldin saqlab olamiz
        old_instance = self.get_object()
        old_data = {
            "name": old_instance.name,
            "status": old_instance.status,
            "room": old_instance.room.name if old_instance.room else None
        }

        # Yangilaymiz
        group = serializer.save()

        # ── Audit Log ──
        new_data = {"name": group.name, "status": group.status, "room": group.room.name if group.room else None}
        _log_audit(self.request, AuditEntityType.GROUP, group.id, AuditAction.UPDATE,
                   old_data=old_data, new_data=new_data)

    # DELETE (O'chirish)
    def perform_destroy(self, instance):
        # ── Audit Log ──
        _log_audit(self.request, AuditEntityType.GROUP, instance.id, AuditAction.DELETE,
                   old_data={"name": instance.name, "status": instance.status}, new_data=None)
        instance.delete()


# Xonalar
class RoomViewSet(viewsets.ModelViewSet):
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Userda organization yo'qligi uchun employee orqali tekshiramiz
        employee = getattr(self.request.user, 'employee', None)
        if not employee or not employee.organization:
            return Room.objects.none()
        return Room.objects.filter(organization=employee.organization)

    def perform_create(self, serializer):
        employee = getattr(self.request.user, 'employee', None)
        if employee and employee.organization:
            serializer.save(
                organization=employee.organization,
                created_by=self.request.user
            )
        else:
            # Agar foydalanuvchi tashkilotga biriktirilmagan bo'lsa, xato qaytaramiz
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"detail": "Siz hech qaysi tashkilotga biriktirilmagansiz!"})


# Kurslar (Lutg'at)
class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseMinimalSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        employee = getattr(self.request.user, 'employee', None)

        if not employee or not employee.organization:
            return Course.objects.none()

            # 3. Faqat shu xodimning tashkilotiga tegishli kurslarni qaytaramiz
        return Course.objects.filter(organization=employee.organization)
    def perform_create(self, serializer):
    # Userning employee profili orqali tashkilotni topamiz
        print(self.request.user)
        employee = getattr(self.request.user, 'employee', None)
        print("employee -> ", employee)
        if employee and employee.organization:
            serializer.save(
                organization=employee.organization,
                created_by=self.request.user
            )
        else:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"detail": "Sizda tashkilot aniqlanmadi, kurs yarata olmaysiz!"})
