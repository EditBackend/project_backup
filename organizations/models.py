from django.db import models
import uuid
from django.utils.text import slugify
from core.validators import uz_phone_validator
from core.models import BaseModel

# BU joyda yangilanishlar bo'lmoqda xushyor bolib kuzatish kerka.

class SuperAdmin(models.Model):
    username = models.CharField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, unique=True)
    address = models.TextField(blank=True)
    password = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=False)

    date_joined = models.DateTimeField(auto_now_add=True)



    def __str__(self):
        return self.username





class Organizations(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    STATUS = (
        ("active", "Aktiv holatda"),
        ("inactive", "Aktiv emas"),
        ("expires", "To'lov muddati yaqin"),
        ("expired", "To'lov muddati tugagan"),
    )
    superadmin = models.ForeignKey('SuperAdmin',on_delete=models.SET_NULL,null=True,blank=True)
    name = models.CharField(max_length=250, verbose_name="Tashkilot nomi")
    logo = models.FileField(upload_to="org/logos/", null=True, blank=True)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, validators=[uz_phone_validator], unique=True)
    status = models.CharField(max_length=20, choices=STATUS, default="active")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        "accounts.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_created_by"
    )

    updated_by = models.ForeignKey(
        "accounts.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_updated_by"
    )
    work_start_time = models.TimeField(null=True, blank=True, verbose_name="Ish boshlanishi")
    work_end_time = models.TimeField(null=True, blank=True, verbose_name="Ish tugashi")
    org_username = models.CharField(max_length=100, unique=True, null=True, blank=True)
    org_password = models.CharField(max_length=255, null=True, blank=True)
    expired_at = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Tashkilot"
        verbose_name_plural = "Tashkilotlar"

class Branch(models.Model):
    organization = models.ForeignKey(
        Organizations,
        on_delete=models.CASCADE,
        related_name="branches",
        null=True,
        blank=True
    )
    name = models.CharField(max_length=250, verbose_name="Filial nomi")
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, validators=[uz_phone_validator], unique=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        "accounts.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_created_by"
    )

    updated_by = models.ForeignKey(
        "accounts.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_updated_by"
    )
    def __str__(self):
        return f"{self.organization.name if self.organization else 'No Org'} - {self.name}"


class Subscriptions(models.Model):
    organization = models.ForeignKey(
        Organizations,
        on_delete=models.CASCADE,
        related_name="subscriptions",
        null=True,      # <--- qo'shildi
        blank=True      # <--- qo'shildi
    )
    plan_type = models.CharField(max_length=20)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    status = models.CharField(max_length=20)
    price = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        "accounts.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_created_by"
    )

    updated_by = models.ForeignKey(
        "accounts.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_updated_by"
    )

    def __str__(self):
        return f"{self.organization.name if self.organization else 'No Org'} - {self.plan_type}"


class OrganizationSettings(models.Model):
    organization = models.OneToOneField(
        Organizations,
        on_delete=models.CASCADE,
        related_name="settings",
        primary_key=True
    )

    PAYMENT_MODE_CHOICES = (
        ("monthly", "Oylik"),
        ("per_lesson", "Darslik"),
        ("package", "Paket"),
    )

    payment_mode = models.CharField(max_length=20, choices=PAYMENT_MODE_CHOICES, default="monthly")

    exclude_trial_students = models.BooleanField(default=True)
    exclude_archived_students = models.BooleanField(default=True)
    include_student_discount = models.BooleanField(default=False)
    apply_discount_to_salary = models.BooleanField(default=False)
    calculate_archived_salary = models.BooleanField(default=False)
    link_salary_to_attendance = models.BooleanField(default=True)

    only_main_teacher_attendance = models.BooleanField(default=False)
    only_attended_lessons = models.BooleanField(default=True)
    calculate_trial_salary = models.BooleanField(default=False)
    include_frozen_students = models.BooleanField(default=False)

    allow_teacher_sms = models.BooleanField(default=False)
    hide_student_data_from_teacher = models.BooleanField(default=False)
    attendance_only_during_lesson = models.BooleanField(default=False)
    allow_schedule_overlap = models.BooleanField(default=False)
    show_group_balance = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        "accounts.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_created_by"
    )

    updated_by = models.ForeignKey(
        "accounts.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_updated_by"
    )

    def __str__(self):
        return f"Settings for {self.organization.name}"


class ExamSettings(models.Model):
    organization = models.OneToOneField(
        Organizations,
        on_delete=models.CASCADE,
        related_name="exam_settings",
        primary_key=True
    )

    include_active_students = models.BooleanField(default=True)
    include_trial_students = models.BooleanField(default=False)
    include_archived_students = models.BooleanField(default=False)
    include_frozen_students = models.BooleanField(default=False)
    include_deleted_students = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        "accounts.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_created_by"
    )

    updated_by = models.ForeignKey(
        "accounts.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_updated_by"
    )

    def __str__(self):
        return f"Exam Settings for {self.organization.name}"


# Qolgan modellaringiz (Section, LandingPage, LandingPageSubmission, Tag)
class Section(models.Model):
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        "accounts.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_created_by"
    )

    updated_by = models.ForeignKey(
        "accounts.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_updated_by"
    )

    class Meta:
        db_table = "sections"
        verbose_name = "Section"
        verbose_name_plural = "Sections"
        ordering = ['name']

    def __str__(self):
        return self.name


class LandingPage(models.Model):
    organization = models.ForeignKey(Organizations, on_delete=models.CASCADE, related_name="landing_pages")
    name = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique=True)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True, related_name="landing_branch")
    section = models.ForeignKey('Section', on_delete=models.SET_NULL, null=True, blank=True, related_name="landing_section")
    source = models.CharField(max_length=20, choices=[("telegram", "Telegram"), ("instagram", "Instagram"), ("facebook", "Facebook"), ("website", "Website"), ("offline", "Offline"), ("other", "Boshqa")])
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        "accounts.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_created_by"
    )

    updated_by = models.ForeignKey(
        "accounts.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_updated_by"
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)



