from django.db import models
from core.models import BaseModel
from django.contrib.auth import get_user_model

User = get_user_model()


# ════════════════════════════════════════════════════════════════
#  TASK BOARDS (DOSKALAR)
# ════════════════════════════════════════════════════════════════
class TaskBoard(BaseModel):
    name = models.CharField(max_length=250, verbose_name="Doska nomi")
    description = models.TextField(null=True, blank=True)

    # created_by, organization, branch BaseModel dan avtomatik keladi!

    def __str__(self):
        return self.name


# ════════════════════════════════════════════════════════════════
#  TASK COLUMNS (USTUNLAR)
# ════════════════════════════════════════════════════════════════
class TaskColumn(BaseModel):
    board = models.ForeignKey(TaskBoard, on_delete=models.CASCADE, related_name="columns")
    name = models.CharField(max_length=250)
    position = models.PositiveIntegerField(default=0, help_text="Ustunlarning joylashuv tartibi")

    class Meta:
        ordering = ['position']  # Avtomatik tartibda chiqishi uchun

    def __str__(self):
        return f"{self.board.name} - {self.name}"


# ════════════════════════════════════════════════════════════════
#  TASKS (VAZIFALAR)
# ════════════════════════════════════════════════════════════════
class Task(BaseModel):
    PRIORITY = (
        ("low", "Past"),
        ("medium", "O'rta"),
        ("high", "Yuqori"),
        ("urgent", "Shoshilinch")
    )

    STATUS = (
        ("active", "Jarayonda"),
        ("completed", "Bajarildi"),
        ("archived", "Arxivlandi")
    )

    board = models.ForeignKey(TaskBoard, on_delete=models.CASCADE, related_name="tasks")
    column = models.ForeignKey(TaskColumn, on_delete=models.CASCADE, related_name="tasks")

    title = models.CharField(max_length=500)  # Sarlavha qisqa bo'ladi, TextField kerak emas
    description = models.TextField(null=True, blank=True)

    # 1 ta taskka bir nechta xodimni biriktirish imkoniyati:
    assigned_to = models.ManyToManyField(User, blank=True, related_name="assigned_tasks")

    deadline = models.DateTimeField(null=True, blank=True)  # Ba'zi vazifalarda muddat bo'lmasligi mumkin
    priority = models.CharField(max_length=15, choices=PRIORITY, default="medium")
    status = models.CharField(max_length=15, choices=STATUS, default="active")

    updated_at = models.DateTimeField(auto_now=True)  # Xato to'g'rilandi!

    def __str__(self):
        return self.title


# ════════════════════════════════════════════════════════════════
#  COMMENTS (IZOHLAR)
# ════════════════════════════════════════════════════════════════
class TaskComment(BaseModel):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="comments")
    comment = models.TextField()

    # user = ... O'CHIRILDI. Izoh qoldirgan odam BaseModel'dagi created_by da saqlanadi.

    def __str__(self):
        return f"Comment by {self.created_by} on {self.task}"


# ════════════════════════════════════════════════════════════════
#  NOTIFICATIONS (ESLATMALAR / UYG'OTKICHLAR)
# ════════════════════════════════════════════════════════════════
class TaskNotification(BaseModel):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="notifications")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="task_notifications")
    notify_at = models.DateTimeField()
    is_sent = models.BooleanField(default=False)


# ════════════════════════════════════════════════════════════════
#  BOARD PERMISSIONS (DOSKA RUXSATLARI)
# ════════════════════════════════════════════════════════════════
class BoardPermission(BaseModel):
    """
    Trello'dagi kabi ruxsatlarni Task'ka emas, Doskaga (Board) bergan ma'qul.
    Shunda xodim o'ziga ruxsat berilgan doskadagi ishlarni bemalol boshqaradi.
    """
    board = models.ForeignKey(TaskBoard, on_delete=models.CASCADE, related_name="permissions")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="board_permissions")

    can_create_tasks = models.BooleanField(default=True)
    can_edit_tasks = models.BooleanField(default=True)
    can_delete_tasks = models.BooleanField(default=False)

    class Meta:
        unique_together = ('board', 'user')  # 1 ta odamga 1 ta doskada faqat bitta ruxsat to'plami bo'lishi uchun