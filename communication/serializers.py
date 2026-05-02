from rest_framework import serializers
from .models import SmsTemplates, SmsSchedules, SMSMessages
from .models import SmsProvider


class SmsTemplatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = SmsTemplates
        fields = "__all__"

    def validate_name(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Nomi kamida 3 ta belgidan iborat bo‘lishi kerak")
        return value


class SmsSchedulesSerializer(serializers.ModelSerializer):
    template_name = serializers.CharField(source='template.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    # buyerda nega yangilandi chunki avto sms
    class Meta:
        model = SmsSchedules
        fields = '__all__'
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']

    def validate(self, data):
        if not data.get('send_at') and not data.get('cron_expression'):
            raise serializers.ValidationError("send_at yoki cron_expression dan biri kiritilishi shart")
        if data.get('send_at') and data.get('cron_expression'):
            raise serializers.ValidationError("send_at va cron_expression ikkalasini birga kiritib bo'lmaydi")
        return data

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user.employee
        return super().create(validated_data)




class SMSMessagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = SMSMessages
        fields = "__all__"





class SmsProviderSerializer(serializers.ModelSerializer):
    provider_display = serializers.CharField(source='get_provider_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)

    class Meta:
        model = SmsProvider
        fields = '__all__'
        read_only_fields = ['id', 'created_by', 'balance', 'created_at', 'updated_at']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user.employee
        return super().create(validated_data)


class SmsProviderListSerializer(serializers.ModelSerializer):
    provider_display = serializers.CharField(source='get_provider_display', read_only=True)

    class Meta:
        model = SmsProvider
        fields = '__all__'
