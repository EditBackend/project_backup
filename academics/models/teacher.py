from django.db import models
from core.models import BaseModel
from accounts.models import Employee
from academics.models import Group


class TeacherSalaryRules(BaseModel):
    """ O'qituvchiga har bir o'quvchi uchun to'lanadigan qoidalar """
    teacher = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="salary_rules")

    # Har bir o'quvchi to'lagan summaning necha foizi o'qituvchiga ketadi
    percent_per_student = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Masalan: 50.00 (%)")

    # Yoki har bir o'quvchi uchun qat'iy belgilangan pul
    fixed_bonus_per_student = models.DecimalField(max_digits=12, decimal_places=2, default=0,
                                                  help_text="Masalan: 50000 UZS")

    # Yoki ustoz faqat belgilangan (fiksa) oylik olsa
    fixed_monthly_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.teacher.full_name} ({self.percent_per_student}% | {self.fixed_bonus_per_student})"


class TeacherSalaryCalculations(BaseModel):
    """ Avtomatlashtirilgan oylik hisob-kitob varaqasi (Oylik Tabeli) """
    teacher = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="calculated_salaries")
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, related_name="teacher_salaries")

    # CharField o'rniga haqiqiy DateField! Odatda oyning 1-kuni bilan saqlanadi (2026-05-01)
    calculation_month = models.DateField()

    student_count = models.PositiveIntegerField(default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Qo'lda o'zgartirish ehtimoli uchun izoh
    comment = models.TextField(blank=True, null=True)

    class Meta:
        # Bitta ustozga bitta guruhdan bir oyda faqat 1 marta hisobot shakllanadi.
        unique_together = ('teacher', 'group', 'calculation_month')


class TeacherSalaryPayments(BaseModel):
    """ Haqiqatda berilgan pul (Tranzaksiya) """
    PAYMENT_TYPE = (
        ("cash", "Naqd pul"),
        ("card", "Karta (Humo/Uzcard)"),
        ("transfer", "Bank o'tkazmasi")
    )
    teacher = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="salary_payments")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_date = models.DateField()
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE)
    comment = models.TextField(blank=True, null=True)