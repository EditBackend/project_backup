from rest_framework import serializers

class DebtorStudentSerializer(serializers.Serializer):
    student_id = serializers.UUIDField(source='student.id')
    full_name = serializers.CharField(source='student.full_name')
    phone_number = serializers.CharField(source='student.phone_number')
    debt_amount = serializers.DecimalField(source='balance', max_digits=12, decimal_places=2)
    last_lesson_date = serializers.SerializerMethodField()

    def get_last_lesson_date(self, obj):
        # Eng so'nggi qo'shilgan guruh sanasi
        sg = obj.student.student_groups.order_by('-joined_at').first()
        return sg.joined_at if sg else None

class LeaveReasonReportSerializer(serializers.Serializer):
    reason_name = serializers.CharField()
    student_count = serializers.IntegerField()
    percentage = serializers.DecimalField(max_digits=5, decimal_places=2)

class CRMConversionSerializer(serializers.Serializer):
    source_name = serializers.CharField()
    total_leads = serializers.IntegerField()
    converted_leads = serializers.IntegerField()
    conversion_rate = serializers.DecimalField(max_digits=5, decimal_places=2)