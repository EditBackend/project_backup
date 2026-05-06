from core.models import exam_files_upload_path
from django.db import models
from core.models import BaseModel
from accounts.models import Employee

class LessonTime(BaseModel):
    name = models.CharField(max_length=250)
    code = models.CharField(max_length=200, blank=True)

class LessonSchedule(BaseModel):
    teacher = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="lesson_schedules"
    )
    DAY_TYPE = (
        ("odd", "Odd days"),
        ("even", "Even days"),
        ("every", "EveryDaye")
    )
    group = models.ForeignKey('Group', on_delete=models.CASCADE, related_name="lesson_group")
    day_type = models.CharField(max_length=20, choices=DAY_TYPE)
    start_time = models.TimeField()
    end_time = models.TimeField()


# ============ YANGI MODEL: OnlineLesson ============


class OnlineLesson(BaseModel):
    """Onlayn darslar"""

    CONTENT_TYPE = (
        ('video', 'Video'),
        ('document', 'Hujjat'),
        ('image', 'Rasm'),
        ('link', 'Havola'),
        ('text', 'Matn'),
    )

    # Asosiy
    group = models.ForeignKey('Group', on_delete=models.CASCADE, related_name='online_lessons')
    title = models.CharField(max_length=250)
    description = models.TextField(blank=True, null=True)

    # Kontent turi
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE)

    # Fayllar
    video_url = models.URLField(max_length=500, blank=True, null=True)
    file = models.FileField(upload_to='online_lessons/', blank=True, null=True)
    external_link = models.URLField(max_length=500, blank=True, null=True)
    text_content = models.TextField(blank=True, null=True)

    # Sana va vaqt
    lesson_date = models.DateField()
    duration_minutes = models.PositiveIntegerField(default=0)

    # Status
    is_published = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    # Kim yaratdi
    created_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True,
                                   related_name='online_lessons_created')

    class Meta:
        verbose_name = "Onlayn dars"
        verbose_name_plural = "Onlayn darslar"
        ordering = ['group', 'order', '-lesson_date']

    def __str__(self):
        return f"{self.group.name} - {self.title}"


class Exams(BaseModel):
    group = models.ForeignKey('Group', on_delete=models.CASCADE, related_name="exams_group")
    title = models.CharField(max_length=250)
    exam_date = models.DateField()
    min_score = models.DecimalField(max_digits=12, decimal_places=2)
    max_score = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(null=True, blank=True)
    file = models.FileField(upload_to=exam_files_upload_path, null=True, blank=True)
    created_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name="exam_created")

class ExamResults(BaseModel):
    exam = models.ForeignKey(Exams, on_delete=models.SET_NULL, null=True, related_name="exam")
    student = models.ForeignKey('Student', on_delete=models.SET_NULL, null=True, related_name="exam_res_student")
    score = models.DecimalField(max_digits=12, decimal_places=2)
    comment = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name="exam_res_created")


from django.db import models
from core.models import BaseModel


# (Yuqorida sizning LessonSchedule, OnlineLesson, Exams kabi modellaringiz turadi...)

class Attendance(BaseModel):
    """ O'quvchilar davomati (Yo'qlama) """

    # 'student.StudentGroup' deb string ichida beramiz (Circular Import bo'lmasligi uchun)
    student_group = models.ForeignKey(
        'academics.StudentGroup',
        on_delete=models.CASCADE,
        related_name="attendances"
    )
    lesson_date = models.DateField()
    is_present = models.BooleanField(default=False)

    # DIQQAT: branch, organization, marked_by (created_by) maydonlari
    # BaseModel ichida borligi uchun bu yerda qayta yozilmaydi!

    class Meta:
        # BIZNES MANTIQ: Bitta o'quvchiga bir kunda faqat bitta davomat qo'yilishi shart.
        # Bu qoida adashib 2 marta davomat jo'natilganda bazada dublikat (va pulni 2 marta yechish) oldini oladi.
        unique_together = ('student_group', 'lesson_date')

    def __str__(self):
        status = "Kelgan" if self.is_present else "Kelmadi"
        # hasattr tekshiruvi xatolikni oldini oladi
        student_name = self.student_group.student.full_name if hasattr(self, 'student_group') else "Noma'lum"
        return f"{student_name} - {self.lesson_date} ({status})"