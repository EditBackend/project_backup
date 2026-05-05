from django.db import models
from core.models import BaseModel
from accounts.models import Employee
class SmsTemplates(BaseModel):
    name = models.CharField(max_length=250)
    text = models.TextField()
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name="templates_created")

class SmsSchedules(BaseModel):
    TARGET_TYPE = (
        ("lead", "Lead"),
        ("student", "Student"),
        ("group", "Group"),
        ("debtors", "Debtors"),
    )
    name = models.CharField(max_length=250)
    target_type = models.CharField(max_length=20, choices=TARGET_TYPE)
    target_id = models.UUIDField()
    template = models.ForeignKey(SmsTemplates, on_delete=models.CASCADE, related_name="template")
    send_at = models.DateTimeField(null=True, blank=True, help_text="Bir martalik yuborish vaqti")
    cron_expression = models.CharField(max_length=100, null=True, blank=True, help_text="Takroriy SMS uchun cron ifoda")
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name="schedules_created")


class SMSMessages(BaseModel):
    RECIPENT_TYPE = (
        ("lead", "Lead"),
        ("student", "Student"),
        ("group", "Group"),
        ("debtors", "Debtors"),
        ("employee", "Employee"),
    )
    SEND_TYPE = (
        ("manual", "Manual"),
        ("auto", "Auto"),
    )

    STATUS = (
        ("pending", "Pending"),
        ("sent", "Sent"),
        ("failed", "Failed"),
    )

    recipent_type = models.CharField(max_length=20, choices=RECIPENT_TYPE)
    recipent_id = models.UUIDField()
    phone = models.CharField(max_length=20, validators=[uz_phone_validator])
    text = models.TextField()
    template = models.ForeignKey(SmsTemplates, on_delete=models.SET_NULL, null=True, related_name="SMS_template")
    schedule = models.ForeignKey(SmsSchedules, on_delete=models.SET_NULL, null=True, related_name="schedule")
    send_type = models.CharField(max_length=20, choices=SEND_TYPE)
    status = models.CharField(max_length=20, choices=STATUS)
    sent_at = models.DateTimeField()





class SmsProvider(BaseModel):
    PROVIDER_CHOICES = (
        ('playmobile', 'PlayMobile'),
        ('eskiz', 'Eskiz'),
    )

    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES, unique=True)
    email = models.EmailField()
    password = models.CharField(max_length=255)
    nickname = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="SMS balans")
    created_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name="providers_created")

    class Meta:
        db_table = 'sms_provider'
        verbose_name = 'SMS Provider'
        verbose_name_plural = 'SMS Providers'

    def __str__(self):
        return f"{self.get_provider_display()} - {self.email}"
    




















