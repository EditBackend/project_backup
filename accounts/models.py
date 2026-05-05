from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, Group
from core.models import BaseModel, employee_avatar_upload_path, Gender
from organizations.models import Organizations, Branch


class UserManager(BaseUserManager):
    # Odatda SaaS tizimlarda username emas, phone yoki email orqali login qilinadi.
    # Agar phone orqali login qilmoqchi bo'lsangiz, buni to'g'rilashingiz kerak bo'ladi.
    def create_user(self, username, email=None, password=None, **extra_fields):
        if not username:
            raise ValueError('Username majburiy')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, email, password, **extra_fields)


class User(AbstractUser):
    # is_active va email AbstractUser ning o'zida bor, ularni qayta yozmaymiz!
    phone = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=150)
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=Gender.choices, null=True, blank=True)

    # RELATED_NAME lar to'g'rilandi
    organization = models.ForeignKey(Organizations, on_delete=models.CASCADE, null=True, blank=True,
                                     related_name="users")
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True, related_name="users")

    # Agar rollarni oson ajratib olmoqchi bo'lsangiz (Groupdan tashqari qulaylik uchun)
    # qo'shimcha maydon qo'shish mumkin:
    ROLE_CHOICES = (
        ('SUPERADMIN', 'Superadmin'),
        ('EMPLOYEE', 'Xodim'),
        ('STUDENT', 'Oquvchi'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='EMPLOYEE')

    objects = UserManager()

    # Agar telefon raqam orqali login qilmoqchi bo'lsangiz buni 'phone' ga o'zgartiring
    USERNAME_FIELD = "phone"

    @property
    def is_superadmin(self):
        return self.role == 'SUPERADMIN'


class Employee(BaseModel):
    # Faqat ishga (HR) oid ma'lumotlar shu yerda turadi
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="employee_profile")
    photo = models.ImageField(upload_to=employee_avatar_upload_path, null=True, blank=True)
    position = models.CharField(max_length=100, null=True, blank=True)
    is_approved = models.BooleanField(default=False)

    # email va is_active olib tashlandi, chunki ular User da bor. Ular doim sinxron ishlashi kerak.

    def __str__(self):
        return f"{self.user.full_name} - {self.position}"

# Custom Role, RolePermission, UserRole modellarini to'liq O'CHIRIB TASHLANG.
# O'rniga Django'ning tayyor 'Group' modelini ishlating.