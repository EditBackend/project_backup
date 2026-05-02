import uuid
import os
from django.db import models
# from organizations.models import Organizations, Branch

class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey("organizations.Organizations", on_delete=models.CASCADE, related_name="%(class)ss")
    branch = models.ForeignKey("organizations.Branch", on_delete=models.CASCADE, related_name="branch_%(class)ss")
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
        abstract = True

def employee_avatar_upload_path(instance, filename):
    ext = os.path.splitext(filename)[1]

    return (
        f"organizations/{instance.organization_id}/"
        f"employee/{instance.id or uuid.uuid4()}"
        f"/avatar{ext}"
    )

def student_avatar_upload_path(instance, filename):
    ext = os.path.splitext(filename)[1]

    return (
        f"organizations/{instance.organization_id}/"
        f"student/{instance.id or uuid.uuid4()}"
        f"/avatar{ext}"
    )


def exam_files_upload_path(instance, filename):
    ext = os.path.splitext(filename)[1]

    return (
        f"organizations/{instance.organization_id}/"
        f"exam/{instance.id or uuid.uuid4()}"
        f"/file{ext}"
    )

class Gender(models.TextChoices):
    MALE = "M", "Erkak"
    FEMALE = "F", "Ayol"

class Position(models.TextChoices):
    ceo = "ceo", "boshliq"
    adminstrator = "adm", "adminstrator"
    limited_adminstrator = "l/a", "limited_adminstrator"
    marketer = "m","marketer"
    branch_direktor = "b/d", "branch director"
    adminstrator_2 = "adm_2","adminstrator"
    teacher = "teacher", "teacher"
    cashier = "cash", "cashier"














