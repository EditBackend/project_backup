from rest_framework import serializers
from django.utils import timezone
from core.validators import validate_uz_phone
from django.apps import apps
from .models import (
    CRMPipeline, CrmSection, CRMSource, CRMLostReason,
    CRMLead, CRMActivity, CRMLeadLost, CRMLeadNotes, CRMLeadsHistory
)
from django.contrib.auth import get_user_model

User = get_user_model()


# 🔥 Dinamik tashkilot topuvchi yordamchi funksiya
def get_safe_organization(user):
    if not user:
        return None
    if hasattr(user, 'organization') and user.organization:
        return user.organization
    if hasattr(user, 'employee') and user.employee and getattr(user.employee, 'organization', None):
        return user.employee.organization

    # Agar foydalanuvchida umuman bo'lmasa, bazadagi birinchisini oladi
    try:
        org_models = apps.get_app_config('organizations').get_models()
        for model in org_models:
            first_obj = model.objects.first()
            if first_obj:
                return first_obj
    except Exception:
        pass
    return None


class CRMPipelineSerializer(serializers.ModelSerializer):
    class Meta:
        model = CRMPipeline
        fields = ['id', 'name', 'position', 'organization']
        extra_kwargs = {
            'organization': {'required': False, 'allow_null': True}
        }


class CRMLeadsHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CRMLeadsHistory
        fields = '__all__'
        read_only_fields = ['created_by']


class CRMSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CRMSource
        fields = ['id', 'name']

class CRMLeadSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(
        required=True,
        error_messages={'blank': "Lidning to'liq ismini kiritish majburiy."}
    )
    phone_number = serializers.CharField(required=True)

    class Meta:
        model = CRMLead
        fields = [
            'id', 'full_name', 'phone_number', 'gender', 'status', 'temperature',
            'source', 'pipeline', 'section', 'assigned_to', 'expected_course',
            'next_followup_date', 'branch', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'organization', 'created_by']

    def validate_phone_number(self, value):
        value = validate_uz_phone(value)
        request = self.context.get('request')
        if request and request.method == 'POST':
            org = get_safe_organization(request.user)
            if CRMLead.objects.filter(phone_number=value, organization=org).exists():
                raise serializers.ValidationError(
                    "Ushbu telefon raqamli lid sizning bazangizda allaqachon mevcut."
                )
        return value

    def validate_next_followup_date(self, value):
        if value and value < timezone.now():
            raise serializers.ValidationError(
                "Keyingi aloqa sanasi (next_followup_date) o'tgan vaqt bo'lishi mumkin emas. Kelajakdagi vaqtni kiriting."
            )
        return value

    def validate(self, attrs):
        request = self.context.get('request')
        user = request.user if request else None
        org = get_safe_organization(user)

        if not org:
            raise serializers.ValidationError({"non_field_errors": ["Tizimda hech qanday tashkilot topilmadi. Avval tashkilot yarating."]})

        # 🔥 MANA SHU YERDA: Agar pipeline null kelsa, uni section orqali topib bog'laymiz
        section = attrs.get('section')
        if section and not attrs.get('pipeline'):
            attrs['pipeline'] = section.pipeline

        branch = attrs.get('branch')
        if branch and branch.organization != org:
            raise serializers.ValidationError({"branch": "Tanlangan filial sizning tashkilotingizga tegishli emas."})

        pipeline = attrs.get('pipeline')
        if pipeline and pipeline.organization != org:
            raise serializers.ValidationError({"pipeline": "Tanlangan pipeline (bosqich) topilmadi."})

        source = attrs.get('source')
        if source and source.organization != org:
            raise serializers.ValidationError({"source": "Tanlangan manba topilmadi."})

        assigned_to = attrs.get('assigned_to')
        if assigned_to and hasattr(assigned_to, 'organization') and assigned_to.organization != org:
            raise serializers.ValidationError({"assigned_to": "Lidni tayinlamoqchi bo'lgan xodim sizning markazingizda ishlamaydi."})

        return attrs


class CRMActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = CRMActivity
        fields = ['id', 'lead', 'activity_type', 'result', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_lead(self, value):
        request = self.context.get('request')
        org = get_safe_organization(request.user if request else None)
        if value.organization != org:
            raise serializers.ValidationError("Boshqa tashkilot lidiga harakat (activity) qo'sha olmaysiz.")
        return value


class CrmSectionSerializer(serializers.ModelSerializer):
    pipeline_name = serializers.ReadOnlyField(source='pipeline.name')
    course_name = serializers.ReadOnlyField(source='course.name')
    teacher_name = serializers.ReadOnlyField(source='teacher.full_name')

    class Meta:
        model = CrmSection
        fields = "__all__"


class CRMLeadLostSerializer(serializers.ModelSerializer):
    class Meta:
        model = CRMLeadLost
        fields = ['lead', 'reason', 'comment']

    def validate(self, attrs):
        request = self.context.get('request')
        lead = attrs.get('lead')
        org = get_safe_organization(request.user if request else None)

        if lead.organization != org:
            raise serializers.ValidationError({"lead": "Sizga tegishli bo'lmagan lidni rad eta olmaysiz."})

        if CRMLeadLost.objects.filter(lead=lead).exists():
            raise serializers.ValidationError({"lead": "Bu lid allaqachon 'Rad etilgan' (Lost) holatiga o'tkazilgan."})

        return attrs