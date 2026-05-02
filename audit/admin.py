from django.contrib import admin
from django.utils.html import format_html
import json
from .models import AuditLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    # Asosiy ro'yxatda nimalar ko'rinishi
    list_display = (
        'action_time', 
        'get_entity_icon', 
        'entity_type', 
        'action_status', 
        'performed_by_display', 
        'performed_by_role'
    )
    
    # Filtrlash imkoniyatlari
    list_filter = (
        'action', 
        'entity_type', 
        'performed_by_role', 
        'created_at'
    )
    
    # Qidiruv
    search_fields = (
        'entity_id', 
        'performed_by__user__full_name', 
        'performed_by__user__username'
    )
    
    # Faqat o'qish uchun (Audit ma'lumotlarini o'zgartirib bo'lmasligi shart!)
    readonly_fields = (
        'entity_type', 'entity_id', 'action', 
        'old_data_pretty', 'new_data_pretty', 
        'performed_by', 'performed_by_role', 'created_at'
    )
    
    # JSON ma'lumotlarni tahrirlashdan yashiramiz
    exclude = ('old_data', 'new_action', 'updated_at', 'updated_by', 'created_by')

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
            'other': '📦'
        }
        icon = icons.get(obj.entity_type, '📄')
        return format_html('<span style="font-size: 18px;">{}</span>', icon)
    get_entity_icon.short_description = ""

    def action_status(self, obj):
        colors = {
            'create': 'green',
            'update': 'orange',
            'delete': 'red'
        }
        color = colors.get(obj.action, 'black')
        return format_html(
            '<b style="color: {}; text-transform: uppercase;">{}</b>', 
            color, obj.get_action_display()
        )
    action_status.short_description = "Amal"

    def performed_by_display(self, obj):
        if obj.performed_by:
            return format_html('<b>{}</b>', obj.performed_by.user.full_name or obj.performed_by.user.username)
        return "Tizim / Robot"
    performed_by_display.short_description = "Kim tomonidan"

    # JSON ma'lumotlarni chiroyli formatda chiqarish
    def old_data_pretty(self, obj):
        return self._format_json(obj.old_data)
    old_data_pretty.short_description = "Eski ma'lumotlar"

    def new_data_pretty(self, obj):
        # Modelda 'new_action' deb yozilgan ekan, shunga mosladim
        return self._format_json(obj.new_action)
    new_data_pretty.short_description = "Yangi ma'lumotlar"

    def _format_json(self, data):
        if not data:
            return "Ma'lumot yo'q"
        # JSONni chiroyli va tushunarli formatga o'tkazish
        formatted_json = json.dumps(data, indent=4, ensure_ascii=False)
        return format_html('<pre style="background: #f8f9fa; padding: 10px; border-radius: 5px; border: 1px solid #ddd;">{}</pre>', formatted_json)

    # Audit ma'lumotlarini o'chirishni taqiqlash (Xavfsizlik uchun)
    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False