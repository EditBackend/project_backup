from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum
from .models.student import (
    Student, StudentGroup, StudentPricing, StudentBalances,
    StudentTarnsactions, LeaveReason, StudentGroupLeaves,
    StudentFreezes, StudentBalanceHistory, Attendence)
from .models.group import (
    Room, Course, Group, GroupTeacher)
from .models.lesson import (
    LessonTime, LessonSchedule, Exams, ExamResults,
    OnlineLesson
)

# ==================== INLINES (Bir-biriga bog'langan modellar) ====================

class StudentGroupInline(admin.TabularInline):
    model = StudentGroup
    extra = 1

class LessonScheduleInline(admin.TabularInline):
    model = LessonSchedule
    extra = 1

class GroupTeacherInline(admin.TabularInline):
    model = GroupTeacher
    extra = 1

# ==================== STUDENT ADMIN ====================

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('display_photo', 'full_name', 'phone_number', 'get_balance', 'status_colored')
    list_filter = ('status', 'branch', 'created_at')
    search_fields = ('full_name', 'phone_number', 'phone_number2', 'telegram_username')
    inlines = [StudentGroupInline]
    list_per_page = 20

    # Rasmni admin panelda ko'rsatish
    def display_photo(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="40" height="40" style="border-radius: 50%;" />', obj.photo.url)
        return "No Photo"
    display_photo.short_description = "Rasm"

    # Balansni rangli ko'rsatish
    def get_balance(self, obj):
        balance_obj = StudentBalances.objects.filter(student=obj).first()
        if balance_obj:
            color = "green" if balance_obj.balance >= 0 else "red"
            return format_html('<b style="color: {};">{} so\'m</b>', color, balance_obj.balance)
        return "0 so'm"
    get_balance.short_description = "Balans"

    def status_colored(self, obj):
        colors = {
            'active': 'green',
            'frozen': 'blue',
            'inactive': 'red',
            'graduated': 'gold'
        }
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', colors.get(obj.status, 'black'), obj.get_status_display())
    status_colored.short_description = "Status"

# ==================== GROUP ADMIN ====================

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'course', 'room', 'teacher_display', 'student_count', 'status_tag')
    list_filter = ('status', 'course', 'branch', 'room')
    search_fields = ('name',)
    inlines = [GroupTeacherInline, LessonScheduleInline]

    def teacher_display(self, obj):
        teachers = GroupTeacher.objects.filter(group=obj).values_list('teacher__user__first_name', flat=True)
        return ", ".join(teachers) if teachers else "Biriktirilmagan"
    teacher_display.short_description = "O'qituvchi"

    def student_count(self, obj):
        count = StudentGroup.objects.filter(group=obj).count()
        return format_html('<b>{} ta talaba</b>', count)
    student_count.short_description = "Talabalar"

    def status_tag(self, obj):
        color = 'green' if obj.status == 'active' else 'grey'
        return format_html('<span style="background: {}; color: white; padding: 3px 10px; border-radius: 10px;">{}</span>', color, obj.get_status_display())
    status_tag.short_description = "Status"

# ==================== FINANCE (Transactions) ====================

@admin.register(StudentTarnsactions)
class StudentTarnsactionsAdmin(admin.ModelAdmin):
    list_display = ('student', 'transaction_type_display', 'amount_display', 'payment_type', 'transaction_date', 'accepted_by')
    list_filter = ('transaction_type', 'payment_type', 'branch', 'transaction_date')
    search_fields = ('student__full_name', 'comment')
    date_hierarchy = 'transaction_date' # Vaqt bo'yicha qulay navigatsiya

    def transaction_type_display(self, obj):
        colors = {'payment': 'green', 'refund': 'red', 'discount': 'blue'}
        return format_html('<span style="color: {};">{}</span>', colors.get(obj.transaction_type, 'black'), obj.get_transaction_type_display())

    def amount_display(self, obj):
        return format_html('<b>{}</b>', obj.amount)

# ==================== ATTENDANCE (Davomat) ====================

@admin.register(Attendence)
class AttendenceAdmin(admin.ModelAdmin):
    list_display = ('student_name', 'group_name', 'lesson_date', 'status_icon', 'marked_by')
    list_filter = ('lesson_date', 'is_present', 'branch')

    def student_name(self, obj):
        return obj.student_group.student.full_name

    def group_name(self, obj):
        return obj.student_group.group.name

    def status_icon(self, obj):
        if obj.is_present:
            return format_html('<span style="color: green; font-size: 20px;">✔</span>')
        return format_html('<span style="color: red; font-size: 20px;">✘</span>')
    status_icon.short_description = "Bor/Yo'q"

# ==================== ONLINE LESSONS ====================

@admin.register(OnlineLesson)
class OnlineLessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'group', 'content_type', 'lesson_date', 'is_published')
    list_filter = ('content_type', 'is_published', 'group')
    search_fields = ('title', 'description')

# ==================== QOLGANLARINI ODDIY RO'YXATGA OLAMIZ ====================

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'monthly_price', 'lesson_month', 'code')

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'capacity')

admin.site.register(StudentBalances)
admin.site.register(LessonSchedule)
admin.site.register(Exams)
admin.site.register(ExamResults)
admin.site.register(LeaveReason)
admin.site.register(StudentFreezes)