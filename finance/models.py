from accounts.models import Employee  # yoki qayerda bo'lsa
from academics.models.group import Course
from django.db import models
from core.models import BaseModel
from django.conf import settings

class ExpenseCategory(BaseModel):
    name = models.CharField(max_length=250)
    expense_type = models.ForeignKey('DetailedExpense', on_delete=models.SET_NULL,null=True,blank=True,related_name="expense_categories",   # <--- BU YERNI O'ZGARTIRDINGIZ
        verbose_name="Xarajat turi")

class Expenses(BaseModel):
    category = models.ForeignKey(ExpenseCategory, on_delete=models.SET_NULL, null=True, related_name="category")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    expense_date = models.DateTimeField()
    comment = models.TextField()


    recipient = models.CharField(max_length=255, null=True, blank=True, verbose_name="Oluvchi")
    payment_type = models.CharField(max_length=50, choices=[('cash', 'Naqd'), ('card', 'Plastik')], default='cash')
    name = models.CharField(max_length=255, null=True, blank=True, verbose_name="Xarajat nomi")

class MonthlyIncome(BaseModel):
    month = models.DateField()
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    comment = models.TextField(blank=True, null=True)

class Payment(BaseModel):
    PAYMENT_TYPES = (
        ('naqd', 'Naqd'),
        ('plastik', 'Plastik karta'),
        ('payme', 'Payme'),
        ('click', 'Click'),
        ('uzum', 'Uzum'),
        ('humo', 'Humo'),
        ('bank', 'Bank o\'tkazma'),
    )
    name = models.CharField(max_length=50, choices=PAYMENT_TYPES, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
# yechib olish u-n
class Sale(BaseModel):
    customer_name = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    course = models.CharField(max_length=255, blank=True, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    debt_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    sale_date = models.DateTimeField(auto_now_add=True)
    month = models.DateField()
    comment = models.TextField(blank=True, null=True)
# xarajatlar
class ExpenseSubcategory(BaseModel):
    CATEGORY_TYPES = (
        ('kommunal', 'Kommunal'),
        ('kantselyar', 'Kantselyar'),
        ('arenda', 'Arenda'),
        ('ish_haqi', 'Ish haqi'),
    )
    category = models.ForeignKey(ExpenseCategory, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=50, choices=CATEGORY_TYPES)

class DetailedExpense(BaseModel):
    EXPENSE_TYPES = (
        ('yangi_xarajat', 'Yangi xarajat'),
        ('to\'lov_turi', "To'lov turi"),
        ('summa', 'Summa'),
    )
    subcategory = models.ForeignKey(ExpenseSubcategory, on_delete=models.CASCADE, related_name='detailed_expenses',null=True, blank=True)
    expense_type = models.CharField(max_length=50, choices=EXPENSE_TYPES,null=True, blank=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    payment_type = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateTimeField()
    comment = models.TextField(blank=True, null=True)


class Bonus(BaseModel):
    BONUS_TYPES = (
        ('course_percent', 'Kurs foizi'),
        ('individual', 'Individual'),
        ('student', 'Talaba soni'),
        ('fixed', 'Belgilangan'),
    )
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='bonuses')
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    bonus_type = models.CharField(max_length=50, choices=BONUS_TYPES)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    month = models.DateField()


class Fine(BaseModel):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='fines')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reason = models.TextField()
    date = models.DateField()


class Salary(BaseModel):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='salaries')
    month = models.DateField()
    base_amount = models.DecimalField(max_digits=12, decimal_places=2)
    bonus_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    fine_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_type = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True)
    is_paid = models.BooleanField(default=False)
    paid_date = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        self.total_amount = self.base_amount + self.bonus_amount - self.fine_amount
        super().save(*args, **kwargs)


class CallLog(BaseModel):
    """Qo'ng'iroqlar jurnali"""
    CALL_TYPE = (
        ('incoming', 'Kiruvchi'),
        ('outgoing', 'Chiquvchi'),
    )

    CALL_STATUS = (
        ('answered', 'Javob berilgan'),
        ('missed', 'O\'tkazib yuborilgan'),
        ('connected_no_answer', 'Bog\'lanildi, javob yo\'q'),
        ('not_connected', 'Bog\'lanilmadi'),
        ('no_answer', 'Javob berilmagan'),
    )

    call_type = models.CharField(max_length=20, choices=CALL_TYPE)
    audio_file = models.FileField(upload_to=call_recording_upload_path, null=True, blank=True)
    call_time = models.DateTimeField()
    caller = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name='calls_made')
    caller_name = models.CharField(max_length=255)
    receiver_phone = models.CharField(max_length=20)
    receiver_name = models.CharField(max_length=255, blank=True)
    gateway = models.CharField(max_length=100)
    is_connected = models.BooleanField(default=False)
    duration = models.IntegerField(default=0)  # sekund
    status = models.CharField(max_length=50, choices=CALL_STATUS)
    result = models.TextField(blank=True)

    class Meta:
        ordering = ['-call_time']
        indexes = [
            models.Index(fields=['-call_time']),
            models.Index(fields=['call_type']),
            models.Index(fields=['status']),
        ]