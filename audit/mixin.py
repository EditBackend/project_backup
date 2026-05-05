from audit.models import AuditLog, AuditAction


class AuditLogMixin:
    """
    Bu Mixin qo'shilgan har qanday ViewSet avtomatik ravishda
    Yaratish, Tahrirlash va O'chirish amallarini AuditLog'ga yozadi.
    """

    def _create_log(self, action, instance, old_data=None, new_data=None):
        user = self.request.user
        if not user or not user.is_authenticated:
            return

        employee = getattr(user, 'employee_profile', None)
        role_name = employee.position if employee else 'Superadmin / Tizim'

        # Model nomini (entity_type) avtomatik aniqlaymiz
        entity_type = instance.__class__.__name__.lower()

        AuditLog.objects.create(
            organization=user.organization,
            branch=getattr(user, 'branch', None),
            created_by=user,
            performed_by_role=role_name,
            entity_type=entity_type,
            entity_id=instance.id,
            action=action,
            old_data=old_data,
            new_data=new_data
        )

    def perform_create(self, serializer):
        instance = serializer.save()
        # Yaratilganda yangi datani olamiz
        new_data = serializer.data
        self._create_log(AuditAction.CREATE, instance, old_data=None, new_data=new_data)

    def perform_update(self, serializer):
        # Tahrirlashdan oldingi datani olib qolamiz
        old_instance = self.get_object()
        old_data = self.get_serializer(old_instance).data

        instance = serializer.save()
        new_data = serializer.data

        self._create_log(AuditAction.UPDATE, instance, old_data=old_data, new_data=new_data)

    def perform_destroy(self, instance):
        old_data = self.get_serializer(instance).data
        self._create_log(AuditAction.DELETE, instance, old_data=old_data, new_data=None)
        instance.delete()