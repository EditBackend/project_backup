from django.db import models
from core.models import BaseModel, Gender
from core.validators import uz_phone_validator
from accounts.models import User
from organizations.models import Organizations, Branch
import uuid
from accounts.models import Employee
from academics.models.group import Course
from django.contrib.auth import get_user_model

User = get_user_model()


class LeadForm(models.Model):
    TYPE_CHOICES = [
        ('lead', 'Lead'),
        ('contact', 'Kontakt'),

    ]

    name = models.CharField(max_length=255, verbose_name="Forma nomi")
    type = models.CharField(max_length=50, choices=TYPE_CHOICES, default='lead')
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Filial")
    pipeline = models.ForeignKey('CRMPipelines', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Bo'lim (Pipeline)")
    source = models.ForeignKey('CRMSource', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Mijoz manbai")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = "Lid Forma"
        verbose_name_plural = "Lid Formalar"

    def __str__(self):
        return self.name


class FormField(models.Model):
    FIELD_TYPE_CHOICES = [
        ('text', 'Matn'),
        ('phone', 'Telefon'),
        ('email', 'Email'),
        ('select', 'Bir necha variantli so\'rovnoma'),
        ('short_text', 'Qisqa izoh'),
        ('long_text', 'Uzoq izoh'),
        ('nps', 'NPS so\'rovnomasi'),
        ('number', 'Raqam'),
        ('date', 'Sana'),
    ]

    lead_form = models.ForeignKey(LeadForm, on_delete=models.CASCADE, related_name='fields')
    label = models.CharField(max_length=255, verbose_name="Maydon nomi")
    field_type = models.CharField(max_length=50, choices=FIELD_TYPE_CHOICES)
    is_required = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    options = models.JSONField(null=True, blank=True)  # select uchun variantlar

    class Meta:
        ordering = ['order']
        verbose_name = "Forma Maydoni"
        verbose_name_plural = "Forma Maydonlari"

    def __str__(self):
        return f"{self.label} ({self.field_type})"


class CrmSection(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=255)

    pipeline = models.ForeignKey(
        "CRMPipelines",
        on_delete=models.CASCADE,
        related_name='sections'
    )

    course = models.ForeignKey(
        Course,   # yoki Group
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='crm_sections'
    )

    teacher = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='crm_sections'
    )

    days = models.CharField(max_length=100, blank=True, null=True)
    time = models.TimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class CRMSource(BaseModel):
    name = models.CharField(max_length=250)

    def __str__(self):
        return self.name


class CRMPipelines(BaseModel):
    name = models.CharField(max_length=250)
    position = models.PositiveIntegerField()

    def __str__(self):
        return self.name


class CRMLead(BaseModel):
    STATUS = (
        ('active', 'Active'),
        ('converted', 'Converted'),
        ('lost', 'Lost')
    )

    full_name = models.CharField(max_length=250)
    phone_number = models.CharField(max_length=20, validators=[uz_phone_validator], unique=True)
    gender = models.CharField(max_length=1, choices=Gender.choices, null=True, blank=True)

    status = models.CharField(max_length=15, choices=STATUS, default='active')

    source = models.ForeignKey(CRMSource, on_delete=models.SET_NULL, null=True, related_name="leads")
    pipline = models.ForeignKey(CRMPipelines, on_delete=models.SET_NULL, null=True, related_name="leads")
    section = models.ForeignKey(CrmSection, on_delete=models.SET_NULL, null=True, related_name="section")

    assigned_to = models.ForeignKey(User, on_delete=models.PROTECT, related_name="assigned_leads")

    expected_course = models.CharField(max_length=150, blank=True)

    # === ORGANIZATION VA BRANCH ===
    organization = models.ForeignKey(
        Organizations,
        on_delete=models.CASCADE,
        related_name="crm_leads",
        null=True,
        blank=True
    )
    branch = models.ForeignKey(
        Branch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="crm_leads"
    )
    # =================================

    updated_at = models.DateTimeField(auto_now=True)
    converted_student_id = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return self.full_name


class CRMActivity(BaseModel):
    ACTIVITY_TYPE = (
        ('call', 'Call'),
        ('sms', 'SMS'),
        ('meeting', 'Meeting'),
    )

    lead = models.ForeignKey(CRMLead, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=10, choices=ACTIVITY_TYPE)
    result = models.CharField(max_length=250, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.lead.full_name} - {self.activity_type}"

class CRMLeadsHistory(BaseModel):
    lead = models.ForeignKey(CRMLead, on_delete=models.CASCADE, related_name='history')

    old_pipeline = models.ForeignKey(
        CRMPipelines,
        on_delete=models.SET_NULL,
        null=True,
        related_name='old_pipeline_history'   # <--- yangi related_name
    )

    new_pipeline = models.ForeignKey(
        CRMPipelines,
        on_delete=models.SET_NULL,
        null=True,
        related_name='new_pipeline_history'   # <--- yangi related_name
    )

    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.lead.full_name} pipeline o'zgartirildi"


class CRMLostReason(BaseModel):
    name = models.CharField(max_length=200)


class CRMLeadLost(BaseModel):
    lead = models.ForeignKey(CRMLead, on_delete=models.CASCADE, related_name="lost_records")
    reason = models.ForeignKey(CRMLostReason, on_delete=models.SET_NULL, null=True)
    comment = models.TextField(blank=True)


class CRMLeadNotes(BaseModel):
    lead = models.ForeignKey(CRMLead, on_delete=models.CASCADE, related_name='notes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="lead_notes")
    note = models.TextField()
