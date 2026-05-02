from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum
from .models import (
    ExpenseCategory, Expenses, MonthlyIncome, Payment,
    Sale, ExpenseSubcategory, DetailedExpense,
    Bonus, Fine, Salary, WorklyIntegration,
    WorklyAttendance, CallLog
)
from core.admin import BaseModelAdmin

# ================== XARAJATLAR VA TO'LOVLAR ==================

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('name_display', 'is_active', 'created_at')
    list_filter = ('is_active',)

    def name_display(self, obj):
        colors = {
            'payme': '#00BFA5', 'click': '#0089D0', 'uzum': '#7000FF',
            'naqd': '#2ECC71', 'plastik': '#3498DB', 'bank': '#F1C40F'
        }
        color = colors.get(obj.name, '#607D8B')
        return format_html('<b style="color: {}; text-transform: uppercase;">{}</b>', color, obj.get_name_display())
    name_display.short_description = "To'lov turi"

# ================== ASOSIY XARAJATLAR (Expenses) ==================
@admin.register(Expenses)
class ExpensesAdmin(BaseModelAdmin):
    list_display = ('name', 'amount_display', 'payment_type', 'expense_date', 'category')
    list_filter = ('payment_type', 'expense_date', 'category')
    search_fields = ('name', 'comment', 'recipient')

    def amount_display(self, obj):
        return format_html('<span style="color: #E74C3C; font-weight: bold;">- {:,.0f} so\'m</span>', obj.amount)
    amount_display.short_description = "Summa"


# ================== BAFURJA XARAJATLAR (DetailedExpense) ==================
@admin.register(DetailedExpense)
class DetailedExpenseAdmin(BaseModelAdmin):
    list_display = ('name', 'amount_display', 'payment_type', 'date', 'subcategory')
    list_filter = ('payment_type', 'date', 'subcategory', 'expense_type')
    search_fields = ('name', 'comment')

    def amount_display(self, obj):
        # DetailedExpense'da amount null bo'lishi mumkinligini hisobga olamiz
        if obj.amount:
            return format_html('<span style="color: #E74C3C; font-weight: bold;">- {:,.0f} so\'m</span>', obj.amount)
        return "0"
    amount_display.short_description = "Summa"

    # Agar models.py da 'date' DateTimeField bo'lsa, avtomatik formatlanadi.
    # Agar formatni o'zgartirmoqchi bo'lsangiz, quyidagicha yozish mumkin:
    def date_info(self, obj):
        return obj.date.strftime("%d.%m.%Y %H:%M") if obj.date else "-"
    date_info.short_description = "Sana"

# ================== SAVDO VA DAROMAD ==================

@admin.register(Sale)
class SaleAdmin(BaseModelAdmin):
    list_display = ('customer_name', 'course', 'amount_paid', 'debt_tag', 'sale_date')
    list_filter = ('month', 'course')
    search_fields = ('customer_name', 'phone')

    def amount_paid(self, obj):
        return format_html('<b style="color: #27AE60;">+ {:,.0f} so\'m</b>', obj.amount)

    def debt_tag(self, obj):
        if obj.debt_amount > 0:
            return format_html('<span style="background: #FDEDEC; color: #CB4335; padding: 2px 8px; border-radius: 4px;">Qarz: {:,.0f}</span>', obj.debt_amount)
        return format_html('<span style="color: #2ECC71;">✅ To\'liq</span>')
    debt_tag.short_description = "Qarz holati"

# ================== ISH HAQI BO'LIMI ==================

@admin.register(Salary)
class SalaryAdmin(BaseModelAdmin):
    list_display = ('employee', 'month_display', 'total_amount_display', 'status_tag', 'paid_date')
    list_filter = ('is_paid', 'month')
    search_fields = ('employee__user__full_name',)

    def month_display(self, obj):
        return obj.month.strftime("%B, %Y")

    def total_amount_display(self, obj):
        return format_html('<b>{:,.0f} so\'m</b>', obj.total_amount)

    def status_tag(self, obj):
        if obj.is_paid:
            return format_html('<span style="color: white; background: #28A745; padding: 3px 10px; border-radius: 12px;">To\'landi</span>')
        return format_html('<span style="color: white; background: #FFC107; padding: 3px 10px; border-radius: 12px;">Kutilmoqda</span>')
    status_tag.short_description = "Holat"

# ================== INTEGRATSIYALAR ==================

@admin.register(WorklyIntegration)
class WorklyIntegrationAdmin(admin.ModelAdmin):
    list_display = ('is_active_tag', 'connection_status', 'last_sync_info')
    readonly_fields = ('last_sync', 'error_message')

    def is_active_tag(self, obj):
        icon = "✅" if obj.is_active else "❌"
        return format_html('{} Active', icon)

    def connection_status(self, obj):
        color = "green" if obj.is_connected else "red"
        text = "Bog'langan" if obj.is_connected else "Xatolik"
        return format_html('<b style="color: {};">{}</b>', color, text)

    def last_sync_info(self, obj):
        return obj.last_sync.strftime("%d.%m.%Y %H:%M") if obj.last_sync else "Hech qachon"

@admin.register(CallLog)
class CallLogAdmin(admin.ModelAdmin):
    list_display = ('type_icon', 'caller_name', 'receiver_phone', 'status_badge', 'duration_display', 'call_time')
    list_filter = ('call_type', 'status', 'call_time')

    def type_icon(self, obj):
        icon = "📥" if obj.call_type == 'incoming' else "📤"
        return format_html('{} {}', icon, obj.get_call_type_display())

    def status_badge(self, obj):
        colors = {'answered': 'green', 'missed': 'red', 'no_answer': 'orange'}
        return format_html('<span style="color: {};">● {}</span>', colors.get(obj.status, 'black'), obj.get_status_display())

    def duration_display(self, obj):
        return f"{obj.duration // 60}m {obj.duration % 60}s"
    duration_display.short_description = "Davomiyligi"

# Qolgan sodda modellarni ro'yxatga olish
admin.site.register([ExpenseCategory, ExpenseSubcategory, Bonus, Fine, MonthlyIncome, WorklyAttendance])