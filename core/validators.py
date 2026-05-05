# core/validators.py
import re
from django.core.exceptions import ValidationError

def validate_uz_phone(value):
    """ O'zbekiston telefon raqamlari uchun tekshiruv """
    # +998901234567 yoki 998901234567 formatini qabul qiladi
    pattern = r'^(?:\+998|998)\d{9}$'
    if not re.match(pattern, value):
        raise ValidationError("Telefon raqami noto'g'ri formatda. Namuna: 998901234567 yoki +998901234567")
    return value

def validate_password_strength(value):
    """ Parol xavfsizligini tekshirish """
    if len(value) < 8:
        raise ValidationError("Parol kamida 8 ta belgidan iborat bo'lishi kerak.")
    if not any(char.isdigit() for char in value):
        raise ValidationError("Parol tarkibida kamida bitta raqam bo'lishi shart.")
    if not any(char.isalpha() for char in value):
        raise ValidationError("Parol tarkibida kamida bitta harf bo'lishi shart.")
    return value