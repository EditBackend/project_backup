from django.contrib import admin
from django.utils.html import format_html
import json
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    # Ro'yxat ko'rinishi
    list_display = (
        'action_time',
        'get_entity_icon',
        'entity_type',
        'action_status',
        'performed_by_display',
        'performed_by_role'
    )

    # Filtrlash
    list_filter = (
        'action',
        'entity_type',
        'performed_by_role',
        'created_at'
    )

    # Qidiruv (performed_by -> created_by ga o'zgartirildi)
    search_fields = (
        'entity_id',
        'created_by__first_name',
        'created_by__last_name',
        'created_by__username'
    )

    # Faqat o'qish uchun (O'zgartirib bo'lmasligi shart!)
    readonly_fields = (
        'entity_type', 'entity_id', 'action',
        'old_data_pretty', 'new_data_pretty',
        'created_by', 'performed_by_role', 'created_at',
        'organization', 'branch'
    )

    # Keraksiz JSON maydonlarni yashiramiz, ularni 'pretty' metodlar orqali ko'ramiz
    exclude = ('old_data', 'new_data', 'updated_at', 'updated_by')

    # --- METODLAR ---

    def action_time(self, obj):
        return obj.created_at.strftime("%d.%m.%Y | %H:%M:%S")

    action_time.short_description = "Vaqt"

    def get_entity_icon(self, obj):
        icons = {
            'lead': '🎯',
            'student': '👨‍🎓',
            'payment': '💰',
            'group': '👥',
            'user': '🔑',
            'employee': '👔',
            'other': '📦'
        }
        icon = icons.get(obj.entity_type, '📄')
        return format_html('<span style="font-size: 18px;">{}</span>', icon)

    get_entity_icon.short_description = ""

    def action_status(self, obj):
        colors = {
            'create': '#28a745',  # Yashil
            'update': '#fd7e14',  # To'q sariq
            'delete': '#dc3545'  # Qizil
        }
        color = colors.get(obj.action, 'black')
        return format_html(
            '<b style="color: {}; text-transform: uppercase;">{}</b>',
            color, obj.get_action_display()
        )

    action_status.short_description = "Amal"

    def performed_by_display(self, obj):
        if obj.created_by:
            # User modelida full_name bor deb hisoblaymiz, bo'lmasa username
            name = getattr(obj.created_by, 'full_name', obj.created_by.username)
            return format_html('<b>{}</b>', name)
        return "Tizim / Avtomat"

    performed_by_display.short_description = "Mas'ul xodim"

    # JSON ma'lumotlarni chiroyli formatda chiqarish
    def old_data_pretty(self, obj):
        return self._format_json(obj.old_data)

    old_data_pretty.short_description = "Eski holati"

    def new_data_pretty(self, obj):
        # Modelingizda 'new_data' deb nomlangani uchun shunga o'zgartirildi
        return self._format_json(obj.new_data)

    new_data_pretty.short_description = "Yangi holati"

    def _format_json(self, data):
        if not data:
            return format_html('<span style="color: #999;">Ma\'lumot yo\'q</span>')
        # JSONni chiroyli formatlash
        formatted_json = json.dumps(data, indent=4, ensure_ascii=False)
        return format_html(
            '<pre style="background: #f8f9fa; padding: 12px; border-radius: 6px; border: 1px solid #ddd; font-family: monospace;">{}</pre>',
            formatted_json
        )

    # --- XAVFSIZLIK ---

    def has_delete_permission(self, request, obj=None):
        # Audit yozuvlarini hech kim (hatto superadmin ham) o'chira olmasligi kerak
        return False

    def has_add_permission(self, request):
        # Auditni qo'lda qo'shib bo'lmaydi
        return False

    def has_change_permission(self, request, obj=None):
        # Audit yozuvlarini o'zgartirib bo'lmaydi
        return False