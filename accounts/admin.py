from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, Employee, Role, RolePermission, UserRole
from django.contrib.auth.models import Permission

# ==================== INLINES ====================

class EmployeeInline(admin.StackedInline):
    model = Employee
    can_delete = False
    verbose_name_plural = 'Ishchi Profili'
    fk_name = 'user'
    exclude = ['created_by', 'updated_by']

class UserRoleInline(admin.TabularInline):
    model = UserRole
    extra = 1

class RolePermissionInline(admin.TabularInline):
    model = RolePermission
    extra = 1
    autocomplete_fields = ['permission']

# ==================== USER ADMIN ====================

@admin.register(User)
class UserAdmin(BaseUserAdmin): # Yoki xato ketsa admin.ModelAdmin
    list_display = ('username', 'full_name', 'phone', 'get_branch', 'get_role', 'is_active', 'is_staff_icon')
    list_filter = ('is_staff', 'is_active', 'branch', 'organization')
    search_fields = ('username', 'full_name', 'phone', 'email')
    ordering = ('-id',)
    inlines = [EmployeeInline, UserRoleInline]

    # ADD_FIELDSETS - bu yangi user qo'shayotganda chiqadigan shakl
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password', 'full_name', 'phone', 'organization', 'branch'),
        }),
    )

    # FIELDSETS - mavjud userni tahrirlashda
    fieldsets = (
        (None, {'fields': ('username', 'password')}), # Parol bu yerda readonly/link bo'ladi
        ('Shaxsiy ma\'lumotlar', {'fields': ('full_name', 'phone', 'email', 'birth_date', 'gender')}),
        ('Tashkilot', {'fields': ('organization', 'branch')}),
        ('Ruxsatlar', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Muhim sanalar', {'fields': ('last_login', 'date_joined')}),
    )

    def get_branch(self, obj):
        return obj.branch.name if obj.branch else "-"
    get_branch.short_description = "Filial"

    def get_role(self, obj):
        # Optimallashtirish uchun select_related yoki prefetch_related ishlatish tavsiya etiladi
        roles = obj.user_roles.all() # related_name orqali chaqirish yaxshiroq
        return ", ".join([r.role.name for r in roles]) if roles else "Rol yo'q"
    get_role.short_description = "Roli"

    def is_staff_icon(self, obj):
        if obj.is_staff:
            # To'g'ri: format_html ga ikkinchi argument sifatida qiymat uzatiladi
            return format_html('<span style="color: green; font-weight: bold;">{}</span>', "✔ Admin")
        return "Oddiy Foydalanuvchi"
    is_staff_icon.short_description = "Status"

# ==================== EMPLOYEE ADMIN ====================

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('display_photo', 'get_full_name', 'position', 'is_approved_status', 'organization', 'branch','is_approved')
    list_filter = ('is_approved', 'is_active', 'position')
    search_fields = ('user__full_name', 'user__username', 'position')
    list_editable = ('is_approved',) # Ro'yxatning o'zida tasdiqlash imkoniyati

    def get_full_name(self, obj):
        return obj.user.full_name
    get_full_name.short_description = "F.I.SH"

    def display_photo(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="40" height="40" style="border-radius: 5px;" />', obj.photo.url)
        return "Rasm yo'q"
    display_photo.short_description = "Foto"

    def is_approved_status(self, obj):
        if obj.is_approved:
            return format_html('<b style="color: green;">Tasdiqlangan</b>')
        return format_html('<b style="color: orange;">Kutilmoqda...</b>')
    is_approved_status.short_description = "Tasdiq"

    def save_model(self, request, obj, form, change):
        admin_employee = getattr(request.user, 'employee', None)
        if not change:
            obj.created_by = admin_employee
        obj.updated_by = admin_employee
        super().save_model(request, obj, form, change)

# ==================== ROLE & PERMISSIONS ====================

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_permissions_count', 'get_users_count')
    search_fields = ('name',)
    inlines = [RolePermissionInline]

    def get_permissions_count(self, obj):
        count = RolePermission.objects.filter(role=obj).count()
        return f"{count} ta ruxsatnoma"
    get_permissions_count.short_description = "Ruxsatlar soni"

    def get_users_count(self, obj):
        count = UserRole.objects.filter(role=obj).count()
        return f"{count} ta foydalanuvchi"
    get_users_count.short_description = "Foydalanuvchilar"
@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    # Autocomplete ishlashi uchun kamida bitta search_field bo'lishi shart
    search_fields = ('name', 'codename')
    list_display = ('name', 'content_type', 'codename')

class RolePermissionInline(admin.TabularInline):
    model = RolePermission  # Sizning oraliq modelingiz
    autocomplete_fields = ['permission']  # Endi bu xato bermaydi
    extra = 1

@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    list_filter = ('role',)
    autocomplete_fields = ['user']