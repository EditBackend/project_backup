from django.contrib import admin
from django.utils.html import format_html
from .models import Organizations, Branch, Subscriptions, TariffPlan


# ==================== INLINES ====================

class BranchInline(admin.TabularInline):
    model = Branch
    extra = 1
    fields = ['id','name', 'phone', 'is_active']


class SubscriptionInline(admin.TabularInline):
    model = Subscriptions
    extra = 1
    # Endi tarif plani va muddati muhim
    fields = ['tariff_plan', 'start_date', 'end_date', 'status', 'paid_amount']


# ==================== ADMIN CLASSES ====================

@admin.register(TariffPlan)
class TariffPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'max_students_display', 'price_per_month', 'is_active']
    list_editable = ['is_active', 'price_per_month']

    def max_students_display(self, obj):
        return obj.max_students if obj.max_students else "Cheksiz"

    max_students_display.short_description = "O'quvchilar limiti"


@admin.register(Organizations)
class OrganizationsAdmin(admin.ModelAdmin):
    # org_username va expired_at o'rniga joriy holat maydonlari ishlatildi
    list_display = ['id','name_with_logo', 'status_badge', 'phone', 'get_current_tariff', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'phone']
    ordering = ['-created_at']

    inlines = [BranchInline, SubscriptionInline]

    fieldsets = (
        ("Asosiy ma'lumotlar", {
            'fields': (('name', 'status'), 'logo')
        }),
        ("Aloqa va Manzil", {
            'fields': ('phone', 'address')
        }),
        ("Ish vaqti", {
            'fields': (('work_start_time', 'work_end_time'),)
        }),
    )

    def name_with_logo(self, obj):
        if obj.logo:
            return format_html(
                '<img src="{}" width="35" height="35" style="border-radius:50%; margin-right:10px; vertical-align:middle; object-fit:cover;"> {}',
                obj.logo.url, obj.name
            )
        return obj.name

    name_with_logo.short_description = "Tashkilot nomi"

    def status_badge(self, obj):
        colors = {
            'active': '#28a745',
            'inactive': '#6c757d',
            'expires': '#ffc107',
            'expired': '#dc3545',
        }
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 10px; border-radius: 10px; font-weight: bold; font-size: 11px;">{}</span>',
            colors.get(obj.status, 'grey'), obj.get_status_display()
        )

    status_badge.short_description = "Status"

    def get_current_tariff(self, obj):
        """ Joriy aktiv tarifni ko'rsatish """
        active_sub = obj.subscriptions.filter(status='active').first()
        if active_sub:
            return f"{active_sub.tariff_plan.name}"
        return "Obuna yo'q"

    get_current_tariff.short_description = "Joriy Tarif"


@admin.register(Subscriptions)
class SubscriptionsAdmin(admin.ModelAdmin):
    list_display = ['organization', 'tariff_plan', 'start_date', 'end_date', 'status']
    list_filter = ['status', 'tariff_plan']
    search_fields = ['organization__name']


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ['name', 'organization', 'phone', 'is_active']
    list_filter = ['is_active', 'organization']
    search_fields = ['name', 'phone']
