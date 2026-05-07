from rest_framework import serializers
from academics.models.teacher import TeacherSalaryRules, TeacherSalaryCalculations, TeacherSalaryPayments


class TeacherSalaryRulesSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.user.full_name', read_only=True)

    class Meta:
        model = TeacherSalaryRules
        fields = '__all__'
        read_only_fields = ['id', 'created_by', 'organization']

    def validate(self, attrs):
        effective_from = attrs.get('effective_from')
        effective_to = attrs.get('effective_to')

        # Mantiqiy tekshiruv
        if effective_to and effective_from >= effective_to:
            raise serializers.ValidationError(
                {"effective_to": "Tugash sanasi boshlanish sanasidan katta bo'lishi kerak."})

        # Foiz 100 dan oshmasligini nazorat qilish
        percent = attrs.get('percent_per_student', 0)
        if percent < 0 or percent > 100:
            raise serializers.ValidationError({"percent_per_student": "Foiz 0 dan 100 gacha bo'lishi shart."})

        return attrs


class TeacherSalaryCalculationsSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.user.full_name', read_only=True)
    group_name = serializers.CharField(source='group.name', read_only=True)

    class Meta:
        model = TeacherSalaryCalculations
        fields = '__all__'
        read_only_fields = ['id', 'created_by', 'organization']


class TeacherSalaryPaymentsSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.user.full_name', read_only=True)

    class Meta:
        model = TeacherSalaryPayments
        fields = '__all__'
        read_only_fields = ['id', 'created_by', 'organization']

    def validate(self, attrs):
        if attrs.get('amount', 0) <= 0:
            raise serializers.ValidationError({"amount": "To'lov summasi 0 dan katta bo'lishi kerak."})
        return attrs