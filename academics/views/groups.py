from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q
from academics.models import Group, Course, Room
from academics.serializers.groups import (
    GroupListSerializer, GroupDetailSerializer, GroupWriteSerializer,
    RoomSerializer, CourseMinimalSerializer
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
        if not user.organization:
            return Group.objects.none()

        # N+1 xatoligini annotate va select_related orqali hal qilamiz
        return Group.objects.filter(organization=user.organization).select_related(
            'course', 'room'
        ).annotate(
            student_count=Count('Sgroup_group', filter=Q(Sgroup_group__left_at__isnull=True), distinct=True),
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
        if not self.request.user.organization: return Room.objects.none()
        return Room.objects.filter(organization=self.request.user.organization)

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization, created_by=self.request.user)


# Kurslar (Lutg'at)
class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseMinimalSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.organization: return Course.objects.none()
        return Course.objects.filter(organization=self.request.user.organization)