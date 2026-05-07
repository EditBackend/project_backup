from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Employee
@receiver(post_save, sender=User)
def create_employee_profile(sender, instance, created, **kwargs):
    if created:
        # 1. AGAR SUPERUSER BO'LSA - EMPLOYEE YARATMAYMIZ
        # Bu createsuperuser buyrug'idagi IntegrityError'ni hal qiladi
        if instance.is_superuser:
            return

        # 2. SUPERADMIN roli bo'lgan oddiy foydalanuvchilar uchun
        if instance.role == 'SUPERADMIN':
            # Eslatma: Agar Employee modelida organization NOT NULL bo'lsa,
            # bu yerda baribir xato berishi mumkin. Shuning uchun null=True qilish tavsiya etiladi.
            Employee.objects.create(
                user=instance,
                position='CEO / Asoschi',
                is_approved=True
            )
        else:
            # Oddiy xodimlar uchun
            Employee.objects.create(
                user=instance,
                is_approved=False
            )