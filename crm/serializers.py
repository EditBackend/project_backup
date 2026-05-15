from rest_framework import serializers
from django.utils import timezone
from core.validators import validate_uz_phone
from .models import (
    CRMPipeline, CrmSection, CRMSource, CRMLostReason,
    CRMLead, CRMActivity, CRMLeadLost, CRMLeadNotes,CRMLeadsHistory
)
from organizations.models import Branch
from django.contrib.auth import get_user_model

User = get_user_model()


# ─── YARDAMCHI SERIALIZERLAR (Read-Only yoki oddiy lug'atlar uchun) ───

class CRMPipelineSerializer(serializers.ModelSerializer):
    class Meta:
        model = CRMPipeline
        fields = ['id', 'name', 'position']

class CRMLeadsHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CRMLeadsHistory
        fields = '__all__'
        read_only_fields = ['created_by']

class CRMSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CRMSource
        fields = ['id', 'name']


# ─── ASOSIY CRM LEAD SERIALIZER (Yaratish va Tahrirlash) ───

class CRMLeadSerializer(serializers.ModelSerializer):
    """ Liddlarni yaratish, tahrirlash va ko'rish uchun umumiy serializer """

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
        # Xavfsizlik uchun bu maydonlarni foydalanuvchi API orqali yubora olmaydi
        read_only_fields = ['id', 'created_at', 'organization', 'created_by']

    def validate_phone_number(self, value):
        # 1. Formatni tekshiramiz
        value = validate_uz_phone(value)

        # 2. Shu tashkilot (maktab) ichida bu raqam oldin kiritilganmi?
        request = self.context.get('request')
        if request and request.method == 'POST':
            if CRMLead.objects.filter(
                    phone_number=value,
                    organization=request.user.organization
            ).exists():
                raise serializers.ValidationError(
                    "Ushbu telefon raqamli lid sizning bazangizda allaqachon mavjud."
                )
        return value

    def validate_next_followup_date(self, value):
        if value and value < timezone.now():
            raise serializers.ValidationError(
                "Keyingi aloqa sanasi (next_followup_date) o'tgan vaqt bo'lishi mumkin emas. Kelajakdagi vaqtni kiriting."
            )
        return value

    def validate(self, attrs):
        """ Global xavfsizlik va biznes mantiq tekshiruvlari """
        request = self.context.get('request')
        org = request.user.organization if request else None

        if not org:
            raise serializers.ValidationError("Tashkilotga biriktirilmagan foydalanuvchi lid qo'sha olmaydi.")

        # XAVFSIZLIK: Boshqa maktabning filialini, pipelinini yoki xodimini tanlab qo'ymasligini tekshiramiz
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
        if assigned_to and assigned_to.organization != org:
            raise serializers.ValidationError(
                {"assigned_to": "Lidni tayinlamoqchi bo'lgan xodim sizning markazingizda ishlamaydi."})

        return attrs


# ─── CRM HARAKATLAR (Qo'ng'iroq, Rad etish) ───

class CRMActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = CRMActivity
        fields = ['id', 'lead', 'activity_type', 'result', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_lead(self, value):
        request = self.context.get('request')
        if value.organization != request.user.organization:
            raise serializers.ValidationError("Boshqa tashkilot lidiga harakat (activity) qo'sha olmaysiz.")
        return value
class CrmSectionSerializer(serializers.ModelSerializer):
    # O'qish (GET) uchun qo'shimcha ma'lumotlar
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

        # 1. Tashkilot daxlsizligi
        if lead.organization != request.user.organization:
            raise serializers.ValidationError({"lead": "Sizga tegishli bo'lmagan lidni rad eta olmaysiz."})

        # 2. Lid allaqachon rad etilgan bo'lsa
        if CRMLeadLost.objects.filter(lead=lead).exists():
            raise serializers.ValidationError({"lead": "Bu lid allaqachon 'Rad etilgan' (Lost) holatiga o'tkazilgan."})

        return attrs