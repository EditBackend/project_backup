from rest_framework import serializers
from .models import User, Employee, Role, RolePermission, UserRole
from organizations.models import Organizations,Branch
from django.db import transaction


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # Muhim maydonlarni oldindan ajratib olamiz
        password = validated_data.pop('password', None)
        gender = validated_data.pop('gender', None)
        birth_date = validated_data.pop('birth_date', None)
        email = validated_data.pop('email',None)
        organization_id = validated_data.pop('organization_id', None)
        branch_id = validated_data.pop('branch_id', None)

        # Qolgan maydonlardan User obyektini yaratamiz
        user = User(**validated_data)

        # Qo'shimcha maydonlarni qo'llaymiz
        if gender is not None:
            user.gender = gender
        if email is not None:
            user.email = email
        if birth_date is not None:
            user.birth_date = birth_date
        if organization_id is not None:
            user.organization_id = organization_id
        if branch_id is not None:
            user.branch_id = branch_id

        # Parolni to'g'ri saqlaymiz
        if password:
            user.set_password(password)

        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)

        # User maydonlarini yangilash
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance


from django.contrib.auth import get_user_model

User = get_user_model()




class EmployeeSerializer(serializers.ModelSerializer):
    """GET, LIST, RETRIEVE uchun serializer"""
    # source='user.full_name' o'rniga MethodField ishlatamiz,
    # chunki bu obyekt ko'rinishidagi xatoni oldini oladi
    full_name = serializers.SerializerMethodField()
    phone = serializers.CharField(source='user.phone', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    birth_date = serializers.DateField(source='user.birth_date', read_only=True)
    gender = serializers.CharField(source='user.gender', read_only=True)

    class Meta:
        model = Employee
        fields = [
            'id',
            'full_name',
            'phone',
            'email',
            'birth_date',
            'gender',
            'position',
            'photo',
            'is_active'
        ]

    def get_full_name(self, obj):
        # obj bu Employee obyekti. Uning user bog'lamasidan ismini olamiz.
        if obj.user and obj.user.full_name:
            return obj.user.full_name
        # Agar full_name bo'sh bo'lsa, email yoki username qaytaramiz
        return obj.user.email if obj.user else "Noma'lum"


class EmployeeCreateSerializer(serializers.ModelSerializer):
    """Yangi xodim yaratish uchun serializer"""
    # ====================== USER MAYDONLARI ======================
    full_name = serializers.CharField(required=True, max_length=150, source='user.full_name')
    phone = serializers.CharField(required=True, max_length=20, source='user.phone')
    email = serializers.EmailField(required=True, source='user.email')
    password = serializers.CharField(write_only=True, required=True, min_length=8, source='user.password')
    birth_date = serializers.DateField(required=False, allow_null=True, source='user.birth_date')
    gender = serializers.CharField(max_length=10, required=False, allow_blank=True, source='user.gender')

    # ForeignKey lar (source olib tashlandi)
    organization = serializers.PrimaryKeyRelatedField(
        queryset=Organizations.objects.all(),
        required=True
    )
    branch = serializers.PrimaryKeyRelatedField(
        queryset=Branch.objects.all(),
        required=False,
        allow_null=True
    )

    # ====================== EMPLOYEE MAYDONLARI ======================
    position = serializers.CharField(max_length=100, required=True)
    photo = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Employee
        fields = [
            'full_name', 'phone', 'email', 'password',
            'birth_date', 'gender', 'organization', 'branch',
            'position', 'photo'
        ]

    @transaction.atomic  # <--- Barcha jarayonni bitta tranzaksiyaga olamiz
    def create(self, validated_data):
        # 1. User ma'lumotlarini ajratib olamiz
        user_data = validated_data.pop('user', {})

        # 2. Tashqi kalit (ForeignKey) obyektlarini ajratib olamiz
        # DRF bu yerda ID emas, tayyor ob'ektlarni qaytaradi
        organization_obj = validated_data.pop('organization', None)
        branch_obj = validated_data.pop('branch', None)

        # 3. User yaratamiz
        user = User.objects.create_user(
            full_name=user_data.get('full_name'),
            phone=user_data.get('phone'),
            email=user_data.get('email'),
            username=user_data.get('email'),           # username = email
            password=user_data.get('password'),
            birth_date=user_data.get('birth_date'),
            gender=user_data.get('gender'),
        )

        # 4. Employee yaratamiz
        employee = Employee.objects.create(
            user=user,
            branch=branch_obj,
            organization=organization_obj,             # Obyektni beramiz
            position=validated_data.pop('position', ''),
            photo=validated_data.pop('photo', None),
            is_active=True,
        )

        return employee

class EmployeeUpdateSerializer(serializers.ModelSerializer):
    """Employee va User maydonlarini qo'lda yangilash (xavfsiz variant)"""

    full_name = serializers.CharField(required=False, max_length=150, source='user.full_name')
    phone = serializers.CharField(required=False, max_length=20, source='user.phone')
    email = serializers.EmailField(required=False, source='user.email')
    birth_date = serializers.DateField(required=False, allow_null=True, source='user.birth_date')
    gender = serializers.CharField(max_length=10, required=False, allow_blank=True, source='user.gender')

    position = serializers.CharField(max_length=100, required=False)
    photo = serializers.ImageField(required=False, allow_null=True)
    is_active = serializers.BooleanField(required=False)

    branch = serializers.PrimaryKeyRelatedField(
        queryset=Branch.objects.all(),
        required=False,
        allow_null=True
    )
    organization = serializers.PrimaryKeyRelatedField(
        queryset=Organizations.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Employee
        fields = [
            'full_name', 'phone', 'email', 'birth_date', 'gender',
            'position', 'photo', 'is_active', 'branch', 'organization'
        ]

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})  # 🔥 MUHIM

        user = instance.user

        # ================= USER =================
        if 'full_name' in user_data:
            user.full_name = user_data['full_name']
        if 'phone' in user_data:
            user.phone = user_data['phone']
        if 'email' in user_data:
            user.email = user_data['email']
        if 'birth_date' in user_data:
            user.birth_date = user_data['birth_date']
        if 'gender' in user_data:
            user.gender = user_data['gender']

        # ================= EMPLOYEE =================
        if 'position' in validated_data:
            instance.position = validated_data['position']
        if 'photo' in validated_data:
            instance.photo = validated_data['photo']
        if 'is_active' in validated_data:
            instance.is_active = validated_data['is_active']
        if 'branch' in validated_data:
            instance.branch = validated_data['branch']
        if 'organization' in validated_data:
            instance.organization = validated_data['organization']

        user.save()
        instance.save()

        return instance

from rest_framework import serializers
from django.db import transaction
from .models import User, Employee

class RegistrationSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=150)
    phone = serializers.CharField(max_length=20)
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        phone = validated_data['phone']
        full_name = validated_data['full_name']
        password = validated_data['password']

        # Foydalanuvchi mavjudligini tekshirish
        user = User.objects.filter(phone=phone).first()
        if user:
            employee, _ = Employee.objects.get_or_create(user=user)
            employee.is_approved = False
            employee.save()
            return employee

        with transaction.atomic():
            # MUHIM: create_user ichida email ham berib ketiladi
            user = User.objects.create_user(
                username=phone,
                phone=phone,
                full_name=full_name,
                password=password,
                email=f"{phone}@example.com"  # Xatolikni yo'qotish uchun vaqtincha shunday qilamiz
            )
            return Employee.objects.create(user=user, is_approved=False)


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'


class RolePermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RolePermission
        fields = '__all__'


class UserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRole
        fields = '__all__'