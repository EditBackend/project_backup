from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Organizations, Branch, Subscriptions
)
from accounts.models import Employee

# ==================== INLINES ====================

class BranchInline(admin.TabularInline):
    model = Branch
    extra = 1
    fields = ['name', 'phone', 'is_active']

class SubscriptionInline(admin.TabularInline):
    model = Subscriptions
    extra = 0
    readonly_fields = ['created_at']

# ==================== ADMIN CLASSES ====================

@admin.register(Organizations)
class OrganizationsAdmin(admin.ModelAdmin):
    list_display = ['name_with_logo', 'org_username', 'status_badge', 'phone', 'expired_at_display']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'org_username', 'phone']
    ordering = ['-created_at']
    
    # Tashkilot ichida hamma narsani boshqarish
    inlines = [BranchInline, SubscriptionInline]
    
    fieldsets = (
        ("Asosiy ma'lumotlar", {
            'fields': (('name', 'status'), 'logo', 'superadmin')
        }),
        ("Aloqa va Manzil", {
            'fields': (('phone', 'org_username'), 'address')
        }),
        ("Ish vaqti va Obuna", {
            'fields': (('work_start_time', 'work_end_time'), 'expired_at')
        }),
    )

    def name_with_logo(self, obj):
        if obj.logo:
            return format_html('<img src="{}" width="35" height="35" style="border-radius:50%; margin-right:10px; vertical-align:middle; object-fit:cover;"> {}', obj.logo.url, obj.name)
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

    def expired_at_display(self, obj):
        if obj.expired_at:
            return obj.expired_at.strftime("%d.%m.%Y")
        return "-"
    expired_at_display.short_description = "Amal qilish muddati"

    def save_model(self, request, obj, form, change):
        employee = Employee.objects.filter(user=request.user).first()
        if not change:
            obj.created_by = employee
        obj.updated_by = employee
        obj.save()
