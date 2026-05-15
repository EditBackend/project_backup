import re
from rest_framework import serializers
from academics.models import (
    Student, StudentGroup, StudentBalances, StudentTransaction,
    StudentGroupLeaves, StudentFreezes, LeaveReason,StudentPricing,StudentBalanceHistory
)

class StudentGroupLeavesSerializer(serializers.ModelSerializer):
    student_name = serializers.ReadOnlyField(source='student.user.full_name')
    group_name = serializers.ReadOnlyField(source='group.name')
    reason_name = serializers.ReadOnlyField(source='reason.name')

    class Meta:
        model = StudentGroupLeaves
        fields = '__all__'
class StudentSerializer(serializers.ModelSerializer):
    balance = serializers.DecimalField(source='balance_info.balance', max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Student
        fields = '__all__'
        read_only_fields = ['id', 'status', 'coins']

    def validate_phone_number(self, value):
        clean_number = re.sub(r'\D', '', value)
        if len(clean_number) < 9:
            raise serializers.ValidationError("Telefon raqami juda qisqa.")

        request = self.context.get('request')
        org = request.user.organization if request else None

        qs = Student.objects.filter(phone_number__icontains=clean_number, organization=org)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise serializers.ValidationError("Bu maktabda ushbu telefon raqam allaqachon mavjud.")
        return clean_number


class StudentGroupSerializer(serializers.ModelSerializer):
    group_name = serializers.CharField(source='group.name', read_only=True)

    class Meta:
        model = StudentGroup
        fields = ['id', 'student', 'group', 'group_name', 'joined_at', 'left_at', 'end_date']


class StudentTransactionSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)

    class Meta:
        model = StudentTransaction
        fields = '__all__'
        read_only_fields = ['id', 'transaction_date']


class StudentFreezeSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentFreezes
        fields = '__all__'

    def validate(self, attrs):
        if attrs['freeze_start_date'] >= attrs['freeze_end_date']:
            raise serializers.ValidationError(
                {"freeze_end_date": "Tugash sanasi boshlanish sanasidan katta bo'lishi shart."})
        return attrs




class StudentPricingSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentPricing
        fields = '__all__'
        read_only_fields = ['organization', 'created_by']

class StudentBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentBalances
        fields = '__all__'
        read_only_fields = ['organization']

class LeaveReasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveReason
        fields = '__all__'

class StudentBalanceHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentBalanceHistory
        fields = '__all__'
        read_only_fields = ['organization']