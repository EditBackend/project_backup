from django.db import models
from core.models import BaseModel
from accounts.models import Employee


class Room(BaseModel):
    name = models.CharField(max_length=250)
    capacity = models.PositiveIntegerField(help_text="Xona sig'imi")

    def __str__(self):
        return self.name


class Course(BaseModel):
    name = models.CharField(max_length=250)
    code = models.CharField(max_length=200, blank=True)
    monthly_price = models.DecimalField(max_digits=10, decimal_places=2)
    # lesson (vaqt) olib tashlandi, chunki vaqt guruhga tegishli.
    lessons_per_month = models.PositiveIntegerField(help_text="Bir oydagi darslar soni (masalan: 12 yoki 13)",default=12)
    duration_months = models.PositiveIntegerField(null=True, blank=True,
                                                  help_text="Kursning umumiy davomiyligi (necha oy)")
    comment = models.TextField(blank=True)
    # created_at BaseModel'da borligi uchun faqat updated_at qoldirildi
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Group(BaseModel):
    STATUS = (
        ("active", "Faol"),
        ("expired", "Yakunlangan"),  # Imlo xatosi to'g'rilandi
        ("archived", "Arxivlangan")
    )
    name = models.CharField(max_length=250)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, related_name="groups")
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, related_name="groups")
    status = models.CharField(max_length=20, choices=STATUS, default="active")
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)  # Ba'zi guruhlar muddatsiz bo'lishi mumkin

    # branch, organization, is_active olib tashlandi. Ular BaseModel va Status ichida hal qilingan.

    def __str__(self):
        return self.name


class GroupTeacher(BaseModel):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="group_teachers")
    teacher = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="teacher_groups")
    start_date = models.DateField()
    # O'qituvchi hali ketmagan bo'lsa bo'sh turadi:
    end_date = models.DateField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Yangilangan vaqt")

    def __str__(self):
        return f"{self.group.name} - {self.teacher}"