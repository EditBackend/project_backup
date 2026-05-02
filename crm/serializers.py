from rest_framework import serializers
from .models import (
    CRMSource, CRMPipelines, CRMLead,
    CRMActivity, CRMLeadsHistory,
    CRMLostReason, CRMLeadLost, CRMLeadNotes,CrmSection
)
from .models import LeadForm, FormField




class FormFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormField
        fields = ['id', 'label', 'field_type', 'is_required', 'order', 'options']
        # lead_form ni yaratish vaqtida majburiy qilmaymiz
        extra_kwargs = {
            'lead_form': {'required': False, 'read_only': True},
            'id': {'read_only': True },
            'order': {'read_only': False}
        }


class LeadFormSerializer(serializers.ModelSerializer):
    fields = FormFieldSerializer(many=True, read_only=True)   # javobda ko'rsatish uchun

    class Meta:
        model = LeadForm
        fields = [
            'id', 'name', 'type', 'branch', 'pipeline', 'source',
            'fields', 'created_at', 'updated_at', 'created_by'
        ]
        read_only_fields = ['created_at', 'updated_at', 'created_by']


# serializers.py

class LeadFormCreateSerializer(serializers.ModelSerializer):
    fields = FormFieldSerializer(many=True, write_only=True)

    class Meta:
        model = LeadForm
        fields = ['name', 'type', 'branch', 'pipeline', 'source', 'fields']

    def create(self, validated_data):
        fields_data = validated_data.pop('fields', [])
        lead_form = LeadForm.objects.create(**validated_data)

        for order, field_data in enumerate(fields_data):
            field_data.pop('lead_form', None)
            field_data.pop('order', None)        # ← Ikki marta kelmasligi uchun

            FormField.objects.create(
                lead_form=lead_form,
                order=order,                     # ← Har doim loopdan olish
                **field_data
            )
        return lead_form

    def update(self, instance, validated_data):
        fields_data = validated_data.pop('fields', None)

        # Asosiy maydonlarni yangilash
        instance.name = validated_data.get('name', instance.name)
        instance.type = validated_data.get('type', instance.type)
        instance.branch = validated_data.get('branch', instance.branch)
        instance.pipeline = validated_data.get('pipeline', instance.pipeline)
        instance.source = validated_data.get('source', instance.source)
        instance.save()

        if fields_data is not None:
            # Hozirgi fieldlarni saqlab qolamiz (id bo'yicha)
            existing_fields = {f.id: f for f in instance.fields.all()}

            for order, field_data in enumerate(fields_data):
                field_id = field_data.get('id')
                field_data.pop('lead_form', None)
                field_data.pop('order', None)        # ← Ikki marta kelmasligi uchun

                if field_id and field_id in existing_fields:
                    # UPDATE
                    field = existing_fields[field_id]
                    field.label = field_data.get('label', field.label)
                    field.field_type = field_data.get('field_type', field.field_type)
                    field.is_required = field_data.get('is_required', field.is_required)
                    field.options = field_data.get('options', field.options)
                    field.order = order
                    field.save()
                else:
                    # CREATE
                    FormField.objects.create(
                        lead_form=instance,
                        order=order,
                        **field_data
                    )

            # Frontdan yuborilmagan eski fieldlarni o‘chirish
            sent_ids = {item.get('id') for item in fields_data if item.get('id') is not None}
            for field_id, field in list(existing_fields.items()):
                if field_id not in sent_ids:
                    field.delete()

        return instance



class CrmSectionSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.name', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)

    class Meta:
        model = CrmSection
        fields = '__all__'



class CRMSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CRMSource
        fields = "__all__"





class CRMPipelinesSerializer(serializers.ModelSerializer):
    class Meta:
        model = CRMPipelines
        fields = "__all__"






# class CRMLeadSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CRMLead
#         fields = "__all__"

#     def validate_full_name(self, value):
#         if len(value) < 3:
#             raise serializers.ValidationError("Ism juda qisqa")
#         return value





class CRMActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = CRMActivity
        fields = "__all__"







class CRMLeadsHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CRMLeadsHistory
        fields = "__all__"






class CRMLostReasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = CRMLostReason
        fields = "__all__"




class CRMLeadLostSerializer(serializers.ModelSerializer):
    class Meta:
        model = CRMLeadLost
        fields = "__all__"





class CRMLeadNotesSerializer(serializers.ModelSerializer):
    class Meta:
        model = CRMLeadNotes
        fields = "__all__"




class CRMLeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = CRMLead
        fields = "__all__"

        extra_kwargs = {
            'assigned_to': {'read_only': True}
        }

    def validate_full_name(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Ism juda qisqa")
        return value

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Biz endi 100% ishonch bilan aytishimiz mumkinki,
        # assigned_to doim bor bo'ladi. Shuning uchun if shart emas.

        # Lekin ma'lumotlar bazasida buzilgan ma'lumot bo'lsa dastur qulamasligi uchun
        # getattr dan foydalanish baribir eng zo'r "best practice" hisoblanadi:

        assigned_user = getattr(instance, 'assigned_to', None)
        if assigned_user:
            representation['assigned_to'] = f"{assigned_user.full_name}".strip()

        return representation











