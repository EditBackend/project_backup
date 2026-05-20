from django.db import models
import uuid
from core.validators import validate_uz_phone
from core.models import BaseModel
from django.core.validators import MinLengthValidator

#3.213.000 ->
# ════════════════════════════════════════════════════════════════
#  YANGI: TARIFLAR JADVALI (Dinamik boshqarish uchun)
# ════════════════════════════════════════════════════════════════
class TariffPlan(models.Model):
    name = models.CharField(max_length=100, verbose_name="Tarif nomi (Start, Basic...)")
    max_students = models.PositiveIntegerField(
        null=True, blank=True,
        verbose_name="Maksimal o'quvchilar soni",
        help_text="Cheksiz bo'lsa bo'sh qoldiring"
    )
    price_per_month = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Oylik to'lov narxi")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        limit = self.max_students if self.max_students else "Cheksiz"
        return f"{self.name} ({limit} o'quvchi) - {self.price_per_month} so'm"
class Holiday(BaseModel):  # models.Model o'rniga loyihadagi BaseModel'ni ishlating
    organization = models.ForeignKey('Organizations', on_delete=models.CASCADE, related_name='holidays')
    name = models.CharField(max_length=200)
    date = models.DateField()

    def __str__(self):
        return f"{self.name} - {self.date}"
# ════════════════════════════════════════════════════════════════
#  TASHKILOT
# ════════════════════════════════════════════════════════════════
class Organizations(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    STATUS = (
        ("active", "Aktiv holatda"),
        ("inactive", "Aktiv emas"),
        ("expires", "To'lov muddati yaqin"),
        ("expired", "To'lov muddati tugagan"),
    )

    name = models.CharField(max_length=250, verbose_name="Tashkilot nomi")
    logo = models.FileField(upload_to="org/logos/", null=True, blank=True)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, validators=[validate_uz_phone], unique=True)
    password = models.CharField(
        max_length=32,
        validators=[
            MinLengthValidator(
                6,
                message="Parol kamida 6 ta belgidan iborat bo‘lishi kerak"
            )
        ]
    )
    status = models.CharField(max_length=20, choices=STATUS, default="active")

    work_start_time = models.TimeField(null=True, blank=True, verbose_name="Ish boshlanishi")
    work_end_time = models.TimeField(null=True, blank=True, verbose_name="Ish tugashi")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Tashkilot"
        verbose_name_plural = "Tashkilotlar"

    # Limitni tekshirish uchun maxsus metod
    def has_student_capacity(self, current_student_count):
        """
        Tashkilotning joriy obunasiga qarab, yangi o'quvchi qo'shish imkoni bormi?
        """
        active_sub = self.subscriptions.filter(status='active').first()
        if not active_sub or not active_sub.tariff_plan:
            return False

        max_limit = active_sub.tariff_plan.max_students
        if max_limit is None:  # Cheksiz tarif
            return True

        return current_student_count < max_limit


# ════════════════════════════════════════════════════════════════
#  OBUNA TIZIMI (Tarif bilan bog'langan)
# ════════════════════════════════════════════════════════════════
class Subscriptions(models.Model):
    organization = models.ForeignKey(
        Organizations, on_delete=models.CASCADE, related_name="subscriptions"
    )
    tariff_plan = models.ForeignKey(
        TariffPlan, on_delete=models.RESTRICT, related_name="subscriptions",
        verbose_name="Tanlangan tarif"
    )
    start_date = models.DateField(verbose_name="Obuna boshlanish sanasi")
    end_date = models.DateField(verbose_name="Obuna tugash sanasi")

    SUB_STATUS = (
        ("active", "Faol"),
        ("expired", "Tugagan"),
        ("cancelled", "Bekor qilingan"),
    )
    status = models.CharField(max_length=20, choices=SUB_STATUS, default="active")

    # Tarif narxi o'zgarsa ham, eski obunalar narxi saqlanib qolishi uchun alohida yozib olinadi
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="To'langan summa")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.organization.name} | {self.tariff_plan.name} | {self.status}"


# ════════════════════════════════════════════════════════════════
#  FILIALLAR (Cheklovlarsiz)
# ════════════════════════════════════════════════════════════════
class Branch(models.Model):
    organization = models.ForeignKey(
        Organizations, on_delete=models.CASCADE, related_name="branches"
    )
    name = models.CharField(max_length=250, verbose_name="Filial nomi")
    address = models.TextField(blank=True)
    # unique=True olib tashlandi, turli tashkilotlar bir xil raqam ishlata olishi uchun
    phone = models.CharField(max_length=20, validators=[validate_uz_phone], blank=True, null=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.organization.name} - {self.name}"

# OrganizationSettings va ExamSettings modellarida mantiqiy xato yo'q,
# ularni o'zingiz yozgan holatda ishlataverishingiz mumkin.