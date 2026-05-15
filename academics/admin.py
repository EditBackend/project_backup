from django.contrib import admin
from django.utils.html import format_html
from .models.student import (
    Student, StudentGroup, StudentBalances,
    LeaveReason, StudentFreezes, StudentTransaction # Transaction qo'shildi
)
from .models.group import (
    Room, Course, Group, GroupTeacher)
from .models.lesson import (
    LessonTime, LessonSchedule, Exams, ExamResults,
    OnlineLesson, Attendance # To'g'ri nom bilan qo'shildi
)

# ==================== INLINES ====================

class StudentGroupInline(admin.TabularInline):
    model = StudentGroup
    extra = 1
    # UUID ishlatilganda autocomplete yordam beradi
    autocomplete_fields = ['student']

class LessonScheduleInline(admin.TabularInline):
    model = LessonSchedule
    extra = 1

class GroupTeacherInline(admin.TabularInline):
    model = GroupTeacher
    extra = 1

# ==================== STUDENT ADMIN ====================

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('id','display_photo', 'full_name', 'phone_number', 'get_balance', 'status_colored')
    list_filter = ('status', 'created_at')
    search_fields = ('full_name', 'phone_number')
    inlines = [StudentGroupInline]
    list_per_page = 20
    # N+1 ning oldini olish uchun
    list_select_related = ('balance_info',)

    def display_photo(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="35" height="35" style="border-radius: 50%; object-fit: cover;" />', obj.photo.url)
        return "—"
    display_photo.short_description = "Rasm"

    def get_balance(self, obj):
        # Related_name orqali murojaat qilish tezroq
        balance_obj = getattr(obj, 'balance_info', None)
        if balance_obj:
            color = "green" if balance_obj.balance >= 0 else "red"
            return format_html('<b style="color: {};">{} so\'m</b>', color, balance_obj.balance)
        return "0 so'm"
    get_balance.short_description = "Balans"

    def status_colored(self, obj):
        colors = {'active': 'green', 'frozen': 'blue', 'inactive': 'red', 'graduated': 'gold'}
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', colors.get(obj.status, 'black'), obj.get_status_display())
    status_colored.short_description = "Status"

# ==================== GROUP ADMIN ====================

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'course', 'room', 'teacher_display', 'student_count', 'status_tag')
    list_filter = ('status', 'course', 'room')
    search_fields = ('name',)
    inlines = [GroupTeacherInline, LessonScheduleInline]
    list_select_related = ('course', 'room')

    def teacher_display(self, obj):
        # Prefetch qilinmagan bo'lsa, bu yerda join ishlatish ma'qul
        teachers = obj.group_teachers.all()
        return ", ".join([t.teacher.full_name for t in teachers]) if teachers else "—"
    teacher_display.short_description = "O'qituvchi"

    def student_count(self, obj):
        # Related_name orqali count
        count = obj.group_students.count()
        return format_html('<b>{} ta</b>', count)
    student_count.short_description = "O'quvchilar"

    def status_tag(self, obj):
        color = 'green' if obj.status == 'active' else '#777'
        return format_html('<span style="background: {}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px;">{}</span>', color, obj.get_status_display())
    status_tag.short_description = "Status"

# ==================== FINANCE & ATTENDANCE (Commentdan chiqarildi) ====================

@admin.register(StudentTransaction)
class StudentTransactionAdmin(admin.ModelAdmin):
    list_display = ('student', 'transaction_type', 'amount', 'payment_type', 'transaction_date')
    list_filter = ('transaction_type', 'payment_type', 'transaction_date')
    search_fields = ('student__full_name',)

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('get_student', 'get_group', 'lesson_date', 'is_present')
    list_filter = ('lesson_date', 'is_present')

    def get_student(self, obj):
        return obj.student_group.student.full_name
    get_student.short_description = "O'quvchi"

    def get_group(self, obj):
        return obj.student_group.group.name
    get_group.short_description = "Guruh"

# ==================== QOLGANLARI ====================

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    # lessons_per_month modelingizdagi nomga to'g'rilandi
    list_display = ('id','name', 'monthly_price', 'lessons_per_month', 'code')

@admin.register(OnlineLesson)
class OnlineLessonAdmin(admin.ModelAdmin):
    list_display = ('id','title', 'group', 'content_type', 'lesson_date', 'is_published')
    list_filter = ('content_type', 'is_published', 'group')

admin.site.register(Room)
admin.site.register(LessonTime)
admin.site.register(Exams)
admin.site.register(ExamResults)
admin.site.register(LeaveReason)
admin.site.register(StudentFreezes)