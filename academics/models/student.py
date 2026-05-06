from django.db import models
from core.models import BaseModel, student_avatar_upload_path
from core.validators import validate_uz_phone


class Student(BaseModel):
    STATUS_CHOICES = (
        ("active", "Faol"),
        ("inactive", "Faol emas (Ketgan)"),
        ("frozen", "Muzlatilgan"),
        ("graduated", "Bitirgan"),
    )
    Gender = (("female", "Ayol"), ("male", "Erkak"))

    full_name = models.CharField(max_length=250)
    photo = models.ImageField(upload_to=student_avatar_upload_path, null=True, blank=True)
    phone_number = models.CharField(max_length=20, validators=[validate_uz_phone])
    phone_number2 = models.CharField(max_length=20, validators=[validate_uz_phone], blank=True, null=True)
    parent_name = models.CharField(max_length=250, blank=True, null=True)
    parent_phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.CharField(max_length=150, blank=True, null=True)
    telegram_username = models.CharField(max_length=150, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    coins = models.PositiveIntegerField(default=0)
    birth_date = models.DateField(null=True, blank=True)
    school = models.CharField(max_length=250, null=True, blank=True)
    extra_info = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default="active")

    class Meta:
        # Multi-tenant: Telefon raqam butun tizimda emas, faqat 1 ta maktab ichida unikal bo'lishi kerak
        unique_together = ('phone_number', 'organization')

    def __str__(self):
        return self.full_name


class StudentGroup(BaseModel):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="student_groups")
    group = models.ForeignKey('Group', on_delete=models.CASCADE, related_name="group_students")
    joined_at = models.DateField()
    left_at = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)


class StudentPricing(BaseModel):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="pricings")
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name="student_pricings")
    price_override = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()


class StudentBalances(BaseModel):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name="balance_info")
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)


class StudentTransaction(BaseModel):  # Nomi to'g'rilandi
    TRANSACTION_TYPE = (
        ("payment", "To'lov"), ("refund", "Pul qaytarish"),
        ("discount", "Chegirma"), ("correction", "Tuzatish")
    )
    PAYMENT_METHOD = (("cash", "Naqd"), ("card", "Karta"), ("transfer", "O'tkazma"))

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="transactions")
    student_group = models.ForeignKey(StudentGroup, on_delete=models.SET_NULL, null=True, blank=True)
    group = models.ForeignKey('Group', on_delete=models.SET_NULL, null=True, blank=True)
    transaction_type = models.CharField(max_length=50, choices=TRANSACTION_TYPE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_type = models.CharField(max_length=30, choices=PAYMENT_METHOD)
    transaction_date = models.DateTimeField(auto_now_add=True)
    comment = models.TextField()


class LeaveReason(BaseModel):
    name = models.CharField(max_length=250)
    is_active = models.BooleanField(default=True)


class StudentGroupLeaves(BaseModel):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="leaves")
    group = models.ForeignKey('Group', on_delete=models.CASCADE)
    student_group = models.ForeignKey(StudentGroup, on_delete=models.CASCADE)
    leave_date = models.DateField()
    leave_reason = models.ForeignKey(LeaveReason, on_delete=models.SET_NULL, null=True)
    comment = models.TextField(null=True, blank=True)
    refund_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)


class StudentFreezes(BaseModel):
    group = models.ForeignKey('Group', on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="freezes")
    freeze_start_date = models.DateField()
    freeze_end_date = models.DateField()
    reason = models.TextField()


class StudentBalanceHistory(BaseModel):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="balance_history")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    base_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    applied_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)