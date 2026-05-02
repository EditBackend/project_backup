from .models import Organizations,Subscriptions,Branch,OrganizationSettings,ExamSettings
from rest_framework import serializers
from .models import LandingPage, LandingPageSubmission,SuperAdmin
from datetime import datetime, timedelta
from django.db import transaction

class SuperAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = SuperAdmin
        fields = ['id', 'username', 'first_name', 'last_name', 'phone', 'address', 'password', 'is_active']
        extra_kwargs = {
            'password': {'write_only': True},
            'id': {'read_only': True}
        }

    def create(self, validated_data):
# hash qilish
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)


class OrganizationSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationSettings
        fields = '__all__'
        read_only_fields = ('organization', 'created_at', 'updated_at')

class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = ['id', 'name', 'address', 'phone', 'is_active']

class OrganizationSerializer(serializers.ModelSerializer):
    settings = OrganizationSettingsSerializer(read_only=True)

    # MUHIM QISMI: Modelingizdagi related_name="branches" orqali ulaymiz
    branches = BranchSerializer(many=True, read_only=True)

    class Meta:
        model = Organizations
        # fields ichiga 'branches' ni qo'shishni unutmang
        fields = [
            'id', 'name', 'logo', 'address', 'phone', 'status',
            'settings', 'branches', 'work_start_time', 'work_end_time',
            'created_at', 'updated_at'
        ]
        read_only_fields = ('created_at',)


from accounts.models import Employee
from django.contrib.auth.hashers import make_password
from accounts.models import User, Employee

class OrganizationCreateSerializer(serializers.ModelSerializer):
    branch_id = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Organizations
        fields = ['id', 'name', 'phone', 'address', 'branch_id']

    def get_branch_id(self, obj):
        branch = Branch.objects.filter(organization=obj).first()
        return branch.id if branch else None

    # organizations/serializers.py ichidagi create metodi
    def create(self, validated_data):
        # ... (tashkilot yaratish qismi) ...
        with transaction.atomic():
            organization = Organizations.objects.create(**validated_data)

            # Filial yaratishdan oldin raqamni tekshiramiz
            branch_phone = validated_data.get('phone')

            # Agar bu raqamli Branch bazada bo'lmasa, keyin yaratadi
            if not Branch.objects.filter(phone=branch_phone).exists():
                Branch.objects.create(
                    name=f"{organization.name} - Asosiy filial",
                    organization=organization,
                    phone=branch_phone
                )
            return organization

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscriptions
        fields = '__all__'
        read_only_fields = ('created_at',)




class ExamSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamSettings
        fields = '__all__'
        read_only_fields = ('organization', 'created_at', 'updated_at')





class LandingPageSerializer(serializers.ModelSerializer):
    submissions_count = serializers.SerializerMethodField()
    full_url = serializers.SerializerMethodField()

    class Meta:
        model = LandingPage
        fields = '__all__'
        read_only_fields = ('organization', 'created_at', 'updated_at')

    def get_submissions_count(self, obj):
        return obj.submissions.count()

    def get_full_url(self, obj):
        # Misol: https://yourcenter.modme.uz/ielts-kursi
        return f"https://yourcenter.modme.uz/{obj.slug}"


class LandingPageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LandingPage
        fields = '__all__'

    def validate_slug(self, value):
        # Slug unikal ekanligini tekshirish
        if LandingPage.objects.filter(slug=value).exists():
            raise serializers.ValidationError("Bu slug allaqachon mavjud.")
        return value


class LandingPageSubmissionSerializer(serializers.ModelSerializer):
    landing_page_name = serializers.CharField(source='landing_page.name', read_only=True)

    class Meta:
        model = LandingPageSubmission
        fields = '__all__'
        read_only_fields = ('branch', 'source', 'created_at')


class LandingPageSubmissionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LandingPageSubmission
        fields = '__all__'


class BillingSubscriptionSerializer(serializers.ModelSerializer):
    days_remaining = serializers.SerializerMethodField()
    is_expiring_soon = serializers.SerializerMethodField()
    organization_name = serializers.CharField(source='organization_id.name', read_only=True)

    class Meta:
        model = Subscriptions
        fields = '__all__'
        read_only_fields = ('created_at',)

    def get_days_remaining(self, obj):
        """Qolgan kunlar"""
        if obj.end_date:
            delta = obj.end_date.date() - datetime.now().date()
            return delta.days if delta.days > 0 else 0
        return 0

    def get_is_expiring_soon(self, obj):
        """Muddat tugashiga yaqinmi (7 kun ichida)"""
        days = self.get_days_remaining(obj)
        return 0 < days <= 7


class BillingCreateSerializer(serializers.ModelSerializer):
    duration_months = serializers.IntegerField(write_only=True, help_text="Muddat (oyda): 1, 3, 6, 12")

    class Meta:
        model = Subscriptions
        fields = '__all__'

    def validate_duration_months(self, value):
        if value not in [1, 3, 6, 12]:
            raise serializers.ValidationError("Faqat 1, 3, 6, yoki 12 oy mumkin")
        return value

    def create(self, validated_data):
        duration = validated_data.pop('duration_months')
        start_date = datetime.now()
        end_date = start_date + timedelta(days=30 * duration)

        subscription = Subscriptions.objects.create(
            start_date=start_date,
            end_date=end_date,
            status='active',
            **validated_data
        )
        return subscription


class BillingStatsSerializer(serializers.Serializer):
    """Billing statistikasi"""
    current_subscription = BillingSubscriptionSerializer()
    total_subscriptions = serializers.IntegerField()
    total_spent = serializers.IntegerField()
    next_payment_date = serializers.DateTimeField()
    days_remaining = serializers.IntegerField()
    status = serializers.CharField()


