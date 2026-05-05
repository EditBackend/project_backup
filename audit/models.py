from django.db import models
from core.models import BaseModel


class AuditEntityType(models.TextChoices):
    LEAD = "lead", "Lead"
    STUDENT = "student", "Student"
    PAYMENT = "payment", "Payment"
    GROUP = "group", "Group"
    USER = "user", "User"
    EMPLOYEE = "employee", "Employee"  # Xodimlar tarixi ham muhim
    OTHER = "other", "Other"


class AuditAction(models.TextChoices):
    CREATE = "create", "Yaratildi"
    UPDATE = "update", "Yangilandi"
    DELETE = "delete", "O'chirildi"


class AuditLog(BaseModel):
    # BaseModel dan organization, branch, created_at va created_by (User) avtomatik keladi!

    entity_type = models.CharField(max_length=30, choices=AuditEntityType.choices)
    entity_id = models.UUIDField(help_text="O'zgartirilgan entity (obyekt) UUID si")
    action = models.CharField(max_length=20, choices=AuditAction.choices)

    old_data = models.JSONField(null=True, blank=True, help_text="O'zgarishdan oldingi holat")
    new_data = models.JSONField(null=True, blank=True, help_text="O'zgarishdan keyingi holat")  # Nom to'g'rilandi

    # performed_by O'CHIRILDI, uning o'rniga BaseModel dagi created_by ishlatiladi.

    # Harakat qilingan paytdagi rolni saqlab qolish yaxshi amaliyot,
    # chunki foydalanuvchining roli kelajakda o'zgarishi mumkin.
    performed_by_role = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name = "Audit Jurnali"
        verbose_name_plural = "Audit Jurnallari"

        # 🔥 MUHIM: Ma'lumotlar bazasi tez ishlashi uchun INDEKSLAR
        indexes = [
            models.Index(fields=['entity_type', 'entity_id']),
            models.Index(fields=['organization', 'created_at']),  # Tashkilot bo'yicha tezkor qidiruv
        ]

    def __str__(self):
        # Admin panelda o'qishga qulay bo'lishi uchun
        user_name = self.created_by.full_name if self.created_by else "Tizim"
        return f"{self.action} | {self.entity_type} ({self.entity_id}) | {user_name}"