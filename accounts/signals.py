from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Employee

@receiver(post_save, sender=User)
def create_employee_profile(sender, instance, created, **kwargs):
    # Agar yangi User yaratilgan bo'lsa
    if created:
        if instance.role == 'SUPERADMIN':
            # Superadmin uchun avtomatik tasdiqlangan CEO profili yaratamiz
            Employee.objects.create(
                user=instance,
                position='CEO / Asoschi',
                is_approved=True
            )
        else:
            # Oddiy xodimlar uchun bo'sh profil yaratiladi (HR keyin to'ldirib tasdiqlaydi)
            Employee.objects.create(
                user=instance,
                is_approved=False
            )