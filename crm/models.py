from django.db import models
from core.models import BaseModel, Gender
from core.validators import validate_uz_phone
from accounts.models import Employee
from academics.models.group import Course
from django.contrib.auth import get_user_model

User = get_user_model()


# ════════════════════════════════════════════════════════════════
#  CRM SOZLAMALARI VA BO'LIMLAR
# ════════════════════════════════════════════════════════════════

class CRMPipeline(BaseModel):
    """ Kanban doskadagi ustunlar (Yangi, Qo'ng'iroq qilindi, Sinov darsi...) """
    name = models.CharField(max_length=250)
    position = models.PositiveIntegerField(default=0, help_text="Ustunlarning joylashuv ketma-ketligi")

    def __str__(self):
        return self.name


class CrmSection(BaseModel):
    """ Qaysi pipeline va qaysi kurs/guruh uchun mo'ljallanganligi """
    name = models.CharField(max_length=255)
    pipeline = models.ForeignKey(CRMPipeline, on_delete=models.CASCADE, related_name='sections')
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True, related_name='crm_sections')
    teacher = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='crm_sections')

    days = models.CharField(max_length=100, blank=True, null=True)
    time = models.TimeField(blank=True, null=True)

    # id va created_at BaseModel dan keladi, qayta yozilmaydi

    def __str__(self):
        return self.name


class CRMSource(BaseModel):
    """ Lid qayerdan keldi? (Instagram, Telegram bot, Tavsiya...) """
    name = models.CharField(max_length=250)

    def __str__(self):
        return self.name


class CRMLostReason(BaseModel):
    """ O'quvchi nega rad etdi? (Qimmat, Uzoq, Boshqa markazga ketdi...) """
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


# ════════════════════════════════════════════════════════════════
#  ASOSIY CRM LEAD MODELI
# ════════════════════════════════════════════════════════════════

class CRMLead(BaseModel):
    STATUS = (
        ('active', 'Aktiv (Jarayonda)'),
        ('converted', 'O\'quvchiga aylandi'),
        ('lost', 'Yo\'qotildi (Rad etdi)')
    )

    TEMPERATURE = (
        ('hot', 'Issiq (Sotib olish ehtimoli yuqori)'),
        ('warm', 'Iliq (O\'ylanmoqda)'),
        ('cold', 'Sovuq (Hali qiziqishi past)'),
    )

    full_name = models.CharField(max_length=250)
    phone_number = models.CharField(max_length=20, validators=[validate_uz_phone])
    gender = models.CharField(max_length=1, choices=Gender.choices, null=True, blank=True)

    status = models.CharField(max_length=15, choices=STATUS, default='active')
    temperature = models.CharField(max_length=10, choices=TEMPERATURE, default='warm')  # Yangi!

    source = models.ForeignKey(CRMSource, on_delete=models.SET_NULL, null=True, related_name="leads")
    pipeline = models.ForeignKey(CRMPipeline, on_delete=models.SET_NULL, null=True, related_name="leads")
    section = models.ForeignKey(CrmSection, on_delete=models.SET_NULL, null=True, blank=True, related_name="leads")

    # Lid tayinlanmagan bo'lishi ham mumkin (Masalan, botdan tushganda), shuning uchun null=True
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name="assigned_leads")
    expected_course = models.CharField(max_length=150, blank=True)

    # CRM Sotuv mantiqi uchun eng muhim maydon!
    next_followup_date = models.DateTimeField(null=True, blank=True, verbose_name="Keyingi aloqa sanasi")

    converted_student_id = models.PositiveIntegerField(null=True, blank=True)

    # organization, branch va updated_by BaseModel dan keladi, qayta yozilmaydi

    class Meta:
        # SaaS tizimlar uchun juda muhim: Bitta tashkilot ichida 1 ta raqam takrorlanmasligi kerak
        unique_together = ('phone_number', 'organization')

    def __str__(self):
        return f"{self.full_name} ({self.phone_number})"


# ════════════════════════════════════════════════════════════════
#  CRM HARAKATLAR VA TARIX
# ════════════════════════════════════════════════════════════════

class CRMActivity(BaseModel):
    """ Qo'ng'iroq qilingani yoki uchrashilgani haqida qisqacha loglar """
    ACTIVITY_TYPE = (
        ('call', 'Qo\'ng\'iroq'),
        ('sms', 'SMS'),
        ('meeting', 'Uchrashuv'),
    )

    lead = models.ForeignKey(CRMLead, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=10, choices=ACTIVITY_TYPE)
    result = models.TextField(blank=True, help_text="Qo'ng'iroq natijasi qanday bo'ldi?")

    # created_by BaseModel orqali kim qilganini avtomatik yozib oladi

    def __str__(self):
        return f"{self.lead.full_name} - {self.activity_type}"


class CRMLeadsHistory(BaseModel):
    """ Kanban doskada ustundan ustunga o'tganda tarixni yozib borish """
    lead = models.ForeignKey(CRMLead, on_delete=models.CASCADE, related_name='history')
    old_pipeline = models.ForeignKey(CRMPipeline, on_delete=models.SET_NULL, null=True,
                                     related_name='old_pipeline_history')
    new_pipeline = models.ForeignKey(CRMPipeline, on_delete=models.SET_NULL, null=True,
                                     related_name='new_pipeline_history')

    # changed_by va changed_at o'rniga BaseModel dagi created_by va created_at ishlatiladi

    def __str__(self):
        return f"{self.lead.full_name}: {self.old_pipeline} -> {self.new_pipeline}"


class CRMLeadLost(BaseModel):
    """ Agar lid rad etsa (lost), qaysi sababga ko'ra rad etgani haqida hisobot """
    lead = models.OneToOneField(CRMLead, on_delete=models.CASCADE, related_name="lost_record")
    reason = models.ForeignKey(CRMLostReason, on_delete=models.SET_NULL, null=True)
    comment = models.TextField(blank=True)


class CRMLeadNotes(BaseModel):
    """ Liddan tushgan ma'lumotlar uchun menejerning shaxsiy eslatmalari """
    lead = models.ForeignKey(CRMLead, on_delete=models.CASCADE, related_name='notes')
    note = models.TextField()
    # user = ForeignKey olib tashlandi, o'rniga BaseModel dagi created_by ishlatiladi