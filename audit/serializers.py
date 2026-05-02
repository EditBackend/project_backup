from rest_framework import serializers
from .models import AuditLog



class AuditLogSerializer(serializers.ModelSerializer):
    """Umumiy audit log"""

    # EmployeeMinimalSerializer ni faqat shu joyda import qilamiz
    def __init__(self, *args, **kwargs):
        from academics.serializers import EmployeeMinimalSerializer
        self.EmployeeSerializer = EmployeeMinimalSerializer
        super().__init__(*args, **kwargs)

    performed_by = serializers.SerializerMethodField()
    action_display = serializers.CharField(source='get_action_display')

    def get_performed_by(self, obj):
        serializer = self.EmployeeSerializer(obj.performed_by)
        return serializer.data

    class Meta:
        model = AuditLog
        fields = '__all__'





# ==================== SERIALIZERS ====================

class AttendanceReportFilterSerializer(serializers.Serializer):
    """Filtrlar uchun"""
    start_date = serializers.DateField(required=True, help_text="Sanadan boshlash")
    end_date = serializers.DateField(required=True, help_text="Sana bo'yicha")
    group_id = serializers.IntegerField(required=False, help_text="Guruh ID (ixtiyoriy)")

    def validate(self, attrs):
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')

        if start_date >= end_date:
            raise serializers.ValidationError({
                'end_date': 'Tugash sanasi boshlanish sanasidan katta bo\'lishi kerak.'
            })

        return attrs


class AttendanceReportSerializer(serializers.Serializer):
    """Hisobot natijalari"""

    indicator_name = serializers.CharField(help_text="Ko'rsatkich nomi")
    description = serializers.CharField(help_text="Tavsif")
    came_once = serializers.IntegerField(help_text="Kelgan talabalar (eng kam bir marta)")
    not_came = serializers.IntegerField(help_text="Kelmagan (martadan ko'p)")
    not_marked = serializers.IntegerField(help_text="Davomat belgilanmagan")
    total = serializers.IntegerField(help_text="Barchasi")