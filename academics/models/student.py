from django.db import models
from core.models import BaseModel, student_avatar_upload_path, exam_files_upload_path
from core.validators import uz_phone_validator
from accounts.models import Employee
from organizations.models import Branch,Organizations

class Student(BaseModel):
    STATUS_CHOICES = (
        ("active", "Faol"),
        ("inactive", "Faol emas (Ketgan)"),
        ("frozen", "Muzlatilgan"),
        ("graduated", "Bitirgan"),
    )

    Gender = (
        ("female", "ayol"),
        ("male", "erkak"),
    )

    full_name = models.CharField(max_length=250)
    photo = models.ImageField(upload_to=student_avatar_upload_path, null=True, blank=True)
    phone_number = models.CharField(max_length=20, validators=[uz_phone_validator], unique=True)
    phone_number2 = models.CharField(max_length=20, validators=[uz_phone_validator, ], unique=True, blank=True, null=True)
    password = models.CharField(max_length=10, blank=True, null=True)
    parent_name = models.CharField(max_length=20, blank=True, null=True)
    parent_phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.CharField(max_length=20, blank=True, null=True)
    telegram_username = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    coins = models.PositiveIntegerField(default=0)
    birth_date = models.DateField(null=True, blank=True)
    school = models.CharField(max_length=250, null=True, blank=True)
    extra_info = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default="active")


class StudentGroup(BaseModel):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="Sgroup_student")
    group = models.ForeignKey('Group', on_delete=models.CASCADE, related_name="Sgroup_group")
    joined_at = models.DateField()
    left_at = models.DateField(null=True,blank=True)
    end_date = models.DateField(null=True,blank=True)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True, blank=True)
    organization = models.ForeignKey(Organizations, on_delete=models.CASCADE, null=True, blank=True)



class StudentPricing(BaseModel):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="Spricing_student")
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name="Spricing_course")
    price_override = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    created_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name="Sprice_created")


class StudentBalances(BaseModel):
    student = models.ForeignKey('Student', on_delete=models.CASCADE, related_name="Sbalances_student")
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True, blank=True)
    # Bu erda 'organizations' edi, 'organization' deb to'g'rilashni tavsiya qilaman,
    # lekin hozircha kodingizga moslab 'organization' deb ishlatamiz
    organization = models.ForeignKey(Organizations, on_delete=models.CASCADE, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True) # auto_now_add emas, auto_now bo'lishi kerak


class StudentTarnsactions(BaseModel):
    TRANSACTION_TYPE = (
        ("payment", "To'lov"),
        ("refund", "Pul qaytarish"),
        ("discount", "Chegirma"),
        ("correction", "Tuzatish")
    )

    PAYMENT_METHOD = (
        ("cash", "Naqd"),
        ("card", "Karta"),
        ("transfer", "O'tkazma")
    )
    student = models.ForeignKey('Student', on_delete=models.CASCADE, related_name="Strans_student")
    # BU YERGA YETISHMAYOTGAN MAYDONLARNI QO'SHAMIZ:
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True, blank=True)
    organization = models.ForeignKey(Organizations, on_delete=models.CASCADE, null=True, blank=True)

    student_group = models.ForeignKey('StudentGroup', on_delete=models.SET_NULL, null=True, related_name="Strans_Sgroup")
    group = models.ForeignKey('Group', on_delete=models.SET_NULL, null=True, related_name="Strans_group")
    transaction_type = models.CharField(max_length=50, choices=TRANSACTION_TYPE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_type = models.CharField(max_length=30, choices=PAYMENT_METHOD)
    transaction_date = models.DateTimeField()
    related_transaction = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="+")
    accepted_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name="Strans_accepted")
    comment = models.TextField()


class LeaveReason(BaseModel):
    name = models.CharField(max_length=250)
    is_active = models.BooleanField(default=True)


class StudentGroupLeaves(BaseModel):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="SGLeave_student")
    group = models.ForeignKey('Group', on_delete=models.CASCADE, related_name="SGLeave_group")
    student_group = models.ForeignKey(StudentGroup, on_delete=models.CASCADE, related_name="SGLeave_Sgroup")
    leave_date = models.DateTimeField()
    leave_reason = models.ForeignKey(LeaveReason, on_delete=models.SET_NULL, null=True, related_name="SGLeave_Lreason")
    comment = models.TextField(null=True, blank=True)
    recalc_balance = models.BooleanField(default=False)
    refound_amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name="SGLeave_created")


class StudentFreezes(BaseModel):
    group = models.ForeignKey('Group', on_delete=models.SET_NULL, null=True, related_name="SFreeze_group")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, related_name="SFreeze_student")
    freeze_start_date = models.DateField()
    freeze_end_date = models.DateField()
    reason = models.TextField()
    recalc_balance = models.BooleanField(default=False)
    created_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name="SFreeze_created")


class StudentBalanceHistory(BaseModel):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="SBHistory_student")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    base_price = models.DecimalField(max_digits=12, decimal_places=2)
    applied_price = models.DecimalField(max_digits=12, decimal_places=2)
    discount = models.DecimalField(max_digits=12, decimal_places=2)


class Attendence(BaseModel):
    student_group = models.ForeignKey(StudentGroup, on_delete=models.CASCADE, related_name="A_Sgroup")
    lesson_date = models.DateField()
    is_present = models.BooleanField(default=False)
    marked_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name="A_marked")
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True, blank=True)
    organization = models.ForeignKey(Organizations, on_delete=models.CASCADE, null=True, blank=True)


    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new and self.is_present: # Talaba darsda bo'lsa pul yechish
            student = self.student_group.student
            # Kurs narxini aniqlash
            price = self.student_group.group.course.price # Misol uchun

            # Balans tarixi yaratish
            StudentBalanceHistory.objects.create(
                student=student,
                amount=-price, # minus bilan
                balance_after=student.balance - price, # joriy balansdan ayirib
                transaction_type='withdraw',
                # MANA BU JOYDA XATO BOR EDI:
                branch_id=student.branch_id,
                organization_id=student.organization_id
            )
