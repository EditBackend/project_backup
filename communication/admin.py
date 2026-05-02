from django.contrib import admin
from django.utils.html import format_html
from .models import SmsTemplates, SmsSchedules, SMSMessages, SmsProvider

# ==================== SMS TEMPLATES ====================

@admin.register(SmsTemplates)
class SmsTemplatesAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_text', 'is_active', 'created_by', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'text')

    def short_text(self, obj):
        return obj.text[:50] + "..." if len(obj.text) > 50 else obj.text
    short_text.short_description = "Shablon matni"

# ==================== SMS SCHEDULES ====================

@admin.register(SmsSchedules)
class SmsSchedulesAdmin(admin.ModelAdmin):
    list_display = ('name', 'target_type_tag', 'template', 'schedule_info', 'is_active')
    list_filter = ('target_type', 'is_active')
    search_fields = ('name', 'target_id')

    def target_type_tag(self, obj):
        colors = {
            'lead': '#2ecc71',
            'student': '#3498db',
            'group': '#9b59b6',
            'debtors': '#e74c3c',
        }
        return format_html(
            '<span style="background: {}; color: white; padding: 2px 8px; border-radius: 4px;">{}</span>',
            colors.get(obj.target_type, 'grey'), obj.get_target_type_display()
        )
    target_type_tag.short_description = "Kimlarga"

    def schedule_info(self, obj):
        if obj.cron_expression:
            return format_html('🔄 <code>{}</code>', obj.cron_expression)
        return format_html('📅 {}', obj.send_at.strftime("%d.%m.%Y %H:%M") if obj.send_at else "Belgilanmagan")
    schedule_info.short_description = "Yuborish vaqti"

# ==================== SMS MESSAGES ====================

@admin.register(SMSMessages)
class SMSMessagesAdmin(admin.ModelAdmin):
    list_display = ('phone', 'recipent_type', 'short_text', 'status_tag', 'send_type_icon', 'sent_at')
    list_filter = ('status', 'recipent_type', 'send_type', 'sent_at')
    search_fields = ('phone', 'text')
    readonly_fields = ('sent_at',)

    def short_text(self, obj):
        return obj.text[:30] + "..." if len(obj.text) > 30 else obj.text
    short_text.short_description = "Xabar matni"

    def status_tag(self, obj):
        colors = {
            'pending': 'orange',
            'sent': 'green',
            'failed': 'red',
        }
        icons = {
            'pending': '⏳',
            'sent': '✅',
            'failed': '❌',
        }
        return format_html(
            '<b style="color: {};">{} {}</b>',
            colors.get(obj.status, 'black'),
            icons.get(obj.status, ''),
            obj.get_status_display()
        )
    status_tag.short_description = "Holat"

    def send_type_icon(self, obj):
        if obj.send_type == 'auto':
            return format_html('<span title="Avtomatik">🤖 Auto</span>')
        return format_html('<span title="Qo\'lda">👤 Manual</span>')
    send_type_icon.short_description = "Turi"

# ==================== SMS PROVIDER ====================

@admin.register(SmsProvider)
class SmsProviderAdmin(admin.ModelAdmin):
    list_display = ('provider_name', 'email', 'get_balance', 'is_active_status','is_active')
    list_editable = ('is_active',)

    def provider_name(self, obj):
        return format_html('<b>{}</b>', obj.get_provider_display())
    provider_name.short_description = "Provayder"

    def get_balance(self, obj):
        color = "green" if obj.balance > 10000 else "red"
        return format_html('<b style="color: {}; font-size: 14px;">{} so\'m</b>', color, obj.balance)
    get_balance.short_description = "SMS Balans"

    def is_active_status(self, obj):
        if obj.is_active:
            return format_html('<span style="color: white; background: green; padding: 2px 10px; border-radius: 10px;">Ishlamoqda</span>')
        return format_html('<span style="color: white; background: red; padding: 2px 10px; border-radius: 10px;">To\'xtatilgan</span>')
    is_active_status.short_description = "Status"