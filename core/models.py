import uuid
import os
from django.db import models
from django.conf import settings  # User modelini chaqirish uchun eng xavfsiz usul


# ════════════════════════════════════════════════════════════════
#  UPLOAD PATH FUNKSIYALAR
# ════════════════════════════════════════════════════════════════

def employee_avatar_upload_path(instance, filename):
    ext = os.path.splitext(filename)[1]
    # MUHIM: Employee modeli organization ni User orqali oladi
    org_id = instance.user.organization_id if instance.user else 'no-org'
    return f"organizations/{org_id}/employee/{instance.id or uuid.uuid4()}/avatar{ext}"


def student_avatar_upload_path(instance, filename):
    ext = os.path.splitext(filename)[1]
    # Student odatda to'g'ridan-to'g'ri organization ga bog'langan bo'ladi
    org_id = getattr(instance, 'organization_id', 'no-org')
    return f"organizations/{org_id}/student/{instance.id or uuid.uuid4()}/avatar{ext}"


def exam_files_upload_path(instance, filename):
    ext = os.path.splitext(filename)[1]
    org_id = getattr(instance, 'organization_id', 'no-org')
    return f"organizations/{org_id}/exam/{instance.id or uuid.uuid4()}/file{ext}"


# ════════════════════════════════════════════════════════════════
#  CHOICES (TANOVCHILAR)
# ════════════════════════════════════════════════════════════════

class Gender(models.TextChoices):
    MALE = "M", "Erkak"
    FEMALE = "F", "Ayol"


# Position (Lavozim) klassi olib tashlandi.


# ════════════════════════════════════════════════════════════════
#  BASE MODEL (Barcha asosiy modellar uchun ota-klass)
# ════════════════════════════════════════════════════════════════

class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Har qanday obyekt qaysi markazga tegishli ekanligi (Majburiy)
    organization = models.ForeignKey(
        "organizations.Organizations",
        on_delete=models.CASCADE,
        related_name="%(class)ss"
    )

    # Filialga bog'lanish (Ixtiyoriy - chunki hamma narsa ham filialniki bo'lmaydi)
    branch = models.ForeignKey(
        "organizations.Branch",
        on_delete=models.CASCADE,
        related_name="%(class)s_branch",
        null=True,
        blank=True
    )

    # Kim yaratdi va qachon? (Employee emas, User ga bog'lanadi)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_created_by"
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_updated_by"
    )

    class Meta:
        abstract = True