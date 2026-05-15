from rest_framework import serializers
from django.db import transaction
from django.contrib.auth import get_user_model
from organizations.models import Organizations, Branch
from .models import Employee
from datetime import date
from core.validators import validate_uz_phone, validate_password_strength
import re

User = get_user_model()


# =======================================================
# 1. READ (O'QISH) UCHUN SERIALIZER
# =======================================================
class EmployeeSerializer(serializers.ModelSerializer):
    """GET, LIST, RETRIEVE uchun serializer"""
    full_name = serializers.ReadOnlyField(source='user.full_name')
    phone = serializers.ReadOnlyField(source='user.phone')
    email = serializers.EmailField(source='user.email')
    birth_date = serializers.DateField(source='user.birth_date')
    gender = serializers.CharField(source='user.gender')

    # Userga ulangan branch va organizationni ko'rsatish
    branch = serializers.PrimaryKeyRelatedField(
        queryset=Branch.objects.all(),
        source='user.branch'
    )
    organization = serializers.PrimaryKeyRelatedField(queryset=Organizations.objects.all(), source='user.organization')
    is_active = serializers.BooleanField(source='user.is_active')

    class Meta:
        model = Employee
        fields = [
            'id', 'full_name', 'phone', 'email', 'birth_date', 'gender',
            'position', 'photo', 'branch', 'organization', 'is_active', 'is_approved'
        ]


# =======================================================
# 2. CREATE (YARATISH) UCHUN SERIALIZER
# =======================================================
class EmployeeCreateSerializer(serializers.Serializer):
    """Yangi xodim yaratish uchun serializer"""
    # User maydonlari
    full_name = serializers.CharField(required=True, error_messages={'blank': "Xodimning ismini kiriting."})
    phone = serializers.CharField(required=True)
    email = serializers.EmailField(
        required=False, allow_blank=True,
        error_messages={'invalid': "Elektron pochta manzili noto'g'ri formatda."}
    )
    password = serializers.CharField(write_only=True, required=True)
    birth_date = serializers.DateField(
        required=False, allow_null=True,
        error_messages={'invalid': "Sana formati noto'g'ri. (Namuna: YYYY-MM-DD)"}
    )
    gender = serializers.CharField(max_length=1, required=False, allow_null=True)
    position = serializers.CharField(required=True, error_messages={'blank': "Lavozimni kiritish majburiy."})

    branch = serializers.PrimaryKeyRelatedField(
        queryset=Branch.objects.all(),
        required=False, allow_null=True,
        error_messages={
            'does_not_exist': "Bunday filial tizimda topilmadi.",
            'incorrect_type': "Filial ID si noto'g'ri formatda."
        }
    )

    def validate_phone(self, value):
        value = validate_uz_phone(value)
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError("Bu telefon raqamli xodim tizimda mavjud. Boshqa raqam kiriting.")
        return value

    def validate_password(self, value):
        return validate_password_strength(value)

    def validate_birth_date(self, value):
        if value:
            # 1. Kelajakdagi sanani kiritmasligi uchun
            if value >= date.today():
                raise serializers.ValidationError("Tug'ilgan sana bugungi kundan oldin bo'lishi shart.")

            # 2. Xodimning yoshi kamida 16 da bo'lishi kerak
            age = date.today().year - value.year - ((date.today().month, date.today().day) < (value.month, value.day))
            if age < 16:
                raise serializers.ValidationError(
                    f"Xodimning yoshi 16 dan kichik bo'lishi mumkin emas. (Kiritilgan yosh: {age})")
        return value

    def validate_gender(self, value):
        if value and value not in ['M', 'F']:
            raise serializers.ValidationError("Jins faqat 'M' (Erkak) yoki 'F' (Ayol) bo'lishi mumkin.")
        return value

    def validate(self, attrs):
        """ Umumiy (Object-level) validatsiya """
        request = self.context.get('request')
        branch = attrs.get('branch')

        # Frontend boshqa maktabning branch_id sini yuborib qolsa, xatolik beramiz
        if branch and request and request.user.organization:
            if branch.organization != request.user.organization:
                raise serializers.ValidationError({
                    "branch": "Tanlangan filial sizning tashkilotingizga tegishli emas."
                })
        return attrs
    @transaction.atomic
    def create(self, validated_data):
        # 1. So'rov yuborayotgan superadmin/menejerni aniqlaymiz (Xavfsizlik uchun)
        request = self.context.get('request')
        current_org = request.user.organization if request else None

        # 2. Employee ma'lumotlarini ajratib olamiz
        position = validated_data.pop('position', '')
        photo = validated_data.pop('photo', None)

        # 3. User ma'lumotlarini tayyorlaymiz
        password = validated_data.pop('password')

        # Odatda telefon raqam orqali login qilinadi, shuning uchun username=phone qilamiz
        validated_data['username'] = validated_data['phone']
        validated_data['organization'] = current_org  # 🔥 Frontenddan emas, backenddan olindi!
        validated_data['role'] = 'EMPLOYEE'

        # 4. Userni yaratamiz
        user = User(**validated_data)
        user.set_password(password)
        user.save()

        # 🔥 DIQQAT: User saqlanganda SIGNAL ishlab avtomatik Employee profil yaratadi!
        # Shuning uchun Employee.objects.create() QILMAYMIZ!
        # Shunchaki yaratilgan profilni topib, ustiga position va photo yozib qoyamiz:

        employee = user.employee_profile
        employee.position = position
        if photo:
            employee.photo = photo
        employee.save()

        return employee


# =======================================================
# 3. UPDATE (YANGILASH) UCHUN SERIALIZER
# =======================================================
class EmployeeUpdateSerializer(serializers.Serializer):
    """Employee va User maydonlarini birgalikda yangilash"""

    full_name = serializers.CharField(required=False, max_length=150)
    phone = serializers.CharField(required=False, max_length=20)
    email = serializers.EmailField(required=False, allow_blank=True)
    birth_date = serializers.DateField(required=False, allow_null=True)
    gender = serializers.CharField(max_length=1, required=False, allow_null=True)
    is_active = serializers.BooleanField(required=False)
    branch = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all(), required=False, allow_null=True)

    position = serializers.CharField(max_length=100, required=False)
    photo = serializers.ImageField(required=False, allow_null=True)

    @transaction.atomic
    def update(self, instance, validated_data):
        user = instance.user

        # User maydonlarini yangilash
        if 'full_name' in validated_data: user.full_name = validated_data['full_name']
        if 'phone' in validated_data: user.phone = validated_data['phone']
        if 'email' in validated_data: user.email = validated_data['email']
        if 'birth_date' in validated_data: user.birth_date = validated_data['birth_date']
        if 'gender' in validated_data: user.gender = validated_data['gender']
        if 'is_active' in validated_data: user.is_active = validated_data['is_active']
        if 'branch' in validated_data: user.branch = validated_data['branch']

        # Employee maydonlarini yangilash
        if 'position' in validated_data: instance.position = validated_data['position']
        if 'photo' in validated_data: instance.photo = validated_data['photo']

        user.save()
        instance.save()

        return instance


# =======================================================
# 4. REGISTRATION (ILK BOR RO'YXATDAN O'TISH)
# =======================================================
class RegistrationSerializer(serializers.Serializer):
    """Faqatgina dastlabki ro'yxatdan o'tish (Superadmin) uchun"""
    full_name = serializers.CharField(
        max_length=150,
        error_messages={
            'required': "Ism va familiyani kiritish majburiy.",
            'blank': "Ism va familiya bo'sh bo'lishi mumkin emas."
        }
    )
    phone = serializers.CharField(max_length=20, required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate_phone(self, value):
        # 1. Formatni tekshiramiz (core dan kelgan funksiya orqali)
        valid_phone = validate_uz_phone(value)

        # 2. Keyin bazada bor-yo'qligini tekshiramiz
        if User.objects.filter(phone=valid_phone).exists():
            raise serializers.ValidationError("Bu telefon raqam allaqachon ro'yxatdan o'tgan.")

        return valid_phone

    def validate_organization_name(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Tashkilot nomi kamida 3 ta harfdan iborat bo'lishi kerak.")
        return value

    def validate_full_name(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Ismingizni to'liq kiriting (kamida 3 ta harf).")
        # Faqat harflar va bo'sh joy qatnashganligini tekshirish
        if not re.match(r'^[a-zA-ZЎўҚқҒғҲҳЁёА-Яа-я\s\']+$', value):
            raise serializers.ValidationError("Ism va familiyada faqat harflar qatnashishi kerak.")
        return value

    def validate_password(self, value):
        # To'g'ridan-to'g'ri core/validators dagi funksiyani qaytaramiz
        return validate_password_strength(value)

    def create(self, validated_data):
        phone = validated_data['phone']
        full_name = validated_data['full_name']
        password = validated_data['password']

        user = User.objects.filter(phone=phone).first()
        if user:
            raise serializers.ValidationError({"phone": "Bu telefon raqam allaqachon mavjud."})

        with transaction.atomic():
            user = User(
                username=phone,
                phone=phone,
                full_name=full_name,
                role='SUPERADMIN'
            )
            user.set_password(password)
            user.save()

            # Bu yerda ham Employee yaratmaymiz! Signal o'zi CEO qilib yaratib oladi.

            return user