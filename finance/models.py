from django.db import models
from core.models import BaseModel
from accounts.models import Employee


class ExpenseCategory(BaseModel):
    """ Xarajat turlari (Arenda, Oylik, Kantselyariya, Kommunal) """
    name = models.CharField(max_length=250)

    def __str__(self):
        return self.name


class Expense(BaseModel):
    """ Barcha kassa chiqimlari (Xarajatlar) bitta jadvalda turadi """
    PAYMENT_METHODS = (
        ('cash', 'Naqd'),
        ('card', 'Plastik karta'),
        ('transfer', "Bank o'tkazmasi"),
    )

    category = models.ForeignKey(ExpenseCategory, on_delete=models.SET_NULL, null=True, related_name="expenses")
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    expense_date = models.DateField()

    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='cash')
    recipient = models.CharField(max_length=255, null=True, blank=True, help_text="Pul kimgaligi/Oluvchi")
    comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.category.name if self.category else 'Boshqa'} - {self.amount}"


# =================================================================
#  XODIMLAR UCHUN BONUS VA JARIMALAR (HR Finance)
# =================================================================
class Bonus(BaseModel):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='bonuses')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    bonus_date = models.DateField()
    reason = models.TextField()


class Fine(BaseModel):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='fines')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    fine_date = models.DateField()
    reason = models.TextField()


class EmployeeSalaryPayment(BaseModel):
    """
    O'qituvchi bo'lmagan xodimlarga (Admin, Farrosh, SMM) to'langan maosh.
    (O'qituvchilar maoshi Academics modulida hisoblanadi!)
    """
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='salary_payments_employee')
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    payment_date = models.DateField()
    payment_method = models.CharField(max_length=20, choices=Expense.PAYMENT_METHODS, default='cash')
    comment = models.TextField(blank=True)