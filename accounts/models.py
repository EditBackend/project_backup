from django.db import models
from django.contrib.auth.models import AbstractUser, Permission, PermissionsMixin, BaseUserManager
from core.models import BaseModel, employee_avatar_upload_path, Gender

from organizations.models import Organizations, Branch
from datetime import date


class UserManager(BaseUserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        if not username:
            raise ValueError('Username majburiy')

        if email:
            email = self.normalize_email(email)

        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser is_staff=True bo\'lishi kerak.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser is_superuser=True bo\'lishi kerak.')

        return self.create_user(username, email, password, **extra_fields)


class User(AbstractUser, PermissionsMixin):
    phone = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1,
                              choices=Gender.choices,
                              null=True,
                              blank=True)

    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL,
                                  null=True, blank=True, related_name="branch")
    organization = models.ForeignKey(Organizations, on_delete=models.CASCADE,
                                        null=True, blank=True, related_name="organization")

    objects = UserManager()
    USERNAME_FIELD = "username"


class Employee(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="employee")
    email = models.EmailField(blank=True, null=True)
    photo = models.ImageField(upload_to=employee_avatar_upload_path,
                              null=True,
                              blank=True)
    position = models.CharField(max_length=100,
                              null=True,
                              blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False)

class Role(BaseModel):
    name = models.CharField(max_length=100)

class RolePermission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="permission_role")
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, related_name="permission")

class UserRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_roles')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="UserRole_role")