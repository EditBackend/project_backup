from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, Employee


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    User modeli uchun admin sozlamalari.
    'autocomplete_fields' ishlashi uchun 'search_fields' majburiy!
    """
    list_display = ('phone', 'full_name', 'role', 'organization', 'branch', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active', 'organization', 'branch')

    # Autocomplete va qidiruv uchun eng muhim qism
    search_fields = ('phone', 'full_name', 'username')
    ordering = ('-date_joined',)

    # Admin panelda Userni tahrirlashda ko'rinadigan maydonlar
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ("Shaxsiy ma'lumotlar", {'fields': ('full_name', 'phone', 'email', 'birth_date', 'gender')}),
        ("Tizim sozlamalari", {'fields': ('role', 'organization', 'branch', 'is_active', 'is_staff', 'is_superuser')}),
        ("Muhim sanalar", {'fields': ('last_login', 'date_joined')}),
    )

    # Yangi user qo'shishda ko'rinadigan maydonlar
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone', 'full_name', 'role', 'password', 'organization', 'is_active'),
        }),
    )


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    """
    Xodimlar (HR) uchun admin sozlamalari.
    """
    list_display = ('get_photo', 'user_display', 'position', 'organization_display', 'is_approved')
    list_filter = ('is_approved', 'position', 'user__organization')
    search_fields = ('user__full_name', 'user__phone', 'position')

    readonly_fields = ('get_full_photo',)

    def user_display(self, obj):
        return obj.user.full_name

    user_display.short_description = "Xodim ismi"

    def organization_display(self, obj):
        return obj.user.organization.name if obj.user.organization else "-"

    organization_display.short_description = "Tashkilot"

    def get_photo(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="40" height="40" style="border-radius:50%; object-fit:cover;" />',
                               obj.photo.url)
        return format_html('<span style="color: #999;">Rasm yo\'q</span>')

    get_photo.short_description = "Rasm"

    def get_full_photo(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="150" style="border-radius:10px;" />', obj.photo.url)
        return "Rasm yuklanmagan"

    get_full_photo.short_description = "Xodim surati"

    # Xodim profilini tahrirlash qismi
    fieldsets = (
        ("Profil", {
            'fields': ('user', 'position', 'is_approved')
        }),
        ("Media", {
            'fields': ('photo', 'get_full_photo')
        }),
        ("Tizim (Avtomatik)", {
            'fields': ('organization', 'branch', 'created_at', 'updated_at'),
            'classes': ('collapse',)  # Yashirin qilib qo'yish uchun
        }),
    )

    # Employee modelida organization/branch BaseModel dan kelsa:
    readonly_fields += ('organization', 'branch', 'created_at', 'updated_at')