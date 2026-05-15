from rest_framework import serializers
from .models import TariffPlan, Organizations, Subscriptions, Branch

class TariffPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = TariffPlan
        fields = '__all__'


class SubscriptionSerializer(serializers.ModelSerializer):
    # Tarif nomini to'g'ridan-to'g'ri qaytarish uchun
    tariff_name = serializers.CharField(source='tariff_plan.name', read_only=True)
    max_students = serializers.IntegerField(source='tariff_plan.max_students', read_only=True)

    class Meta:
        model = Subscriptions
        fields = '__all__'


class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = '__all__'
        # XAVFSIZLIK: Frontenddan kelgan organization ID ga ishonmaymiz, uni faqat o'qiymiz.
        read_only_fields = ['organization']


class OrganizationSerializer(serializers.ModelSerializer):
    # Frontend uchun qulaylik: Tashkilot bilan birga uning filiallari va aktiv obunasini ham qaytaramiz
    active_subscription = serializers.SerializerMethodField()

    def validate(self, attrs):
        # Ish vaqtini tekshirish (Start time < End time)
        start_time = attrs.get('work_start_time', getattr(self.instance, 'work_start_time', None))
        end_time = attrs.get('work_end_time', getattr(self.instance, 'work_end_time', None))

        if start_time and end_time:
            if start_time >= end_time:
                raise serializers.ValidationError({
                    "work_end_time": "Ish tugash vaqti ish boshlanish vaqtidan keyin bo'lishi shart."
                })

        return attrs

    class Meta:
        model = Organizations
        fields = '__all__'
        read_only_fields = ['id', 'status'] # Statusni foydalanuvchi o'zi o'zgartira olmaydi

    def get_active_subscription(self, obj):
        sub = obj.subscriptions.filter(status='active').first()
        if sub:
            return SubscriptionSerializer(sub).data
        return None
