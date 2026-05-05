from rest_framework import serializers
from .models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    # Kim bajarganini aniq ismini chiqarish uchun
    performed_by_name = serializers.CharField(source='created_by.full_name', read_only=True)

    class Meta:
        model = AuditLog
        fields = [
            'id', 'entity_type', 'entity_id', 'action',
            'old_data', 'new_data', 'performed_by_name',
            'performed_by_role', 'created_at'
        ]
        # Barcha maydonlar faqat o'qish uchun!
        read_only_fields = fields