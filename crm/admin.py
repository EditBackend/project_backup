from django.contrib import admin
from django.utils.html import format_html
from .models import (
     CrmSection, CRMSource,
    CRMLead, CRMActivity, CRMLeadsHistory, CRMLostReason,
    CRMLeadLost, CRMLeadNotes
)
from core.admin import BaseModelAdmin

# ==================== INLINES ====================


class CRMActivityInline(admin.TabularInline):
    model = CRMActivity
    extra = 0
    readonly_fields = ['created_at', 'created_by']
    can_delete = False

class CRMLeadNotesInline(admin.StackedInline):
    model = CRMLeadNotes
    extra = 0
    fields = ['user', 'note']

class CRMLeadLostInline(admin.TabularInline):
    model = CRMLeadLost
    extra = 0

# ==================== CRM ADMINS ====================

@admin.register(CRMLead)
class CRMLeadAdmin(BaseModelAdmin):
    list_display = (
        'full_name', 'phone_number', 'status_tag',
        'pipline', 'assigned_to', 'source_tag', 'formatted_created_at'
    )
    list_filter = ('status', 'pipline', 'source', 'branch', 'assigned_to')
    search_fields = ('full_name', 'phone_number')
    autocomplete_fields = ['assigned_to', 'section']

    # Lid ichiga kirganda barcha harakatlar va eslatmalarni ko'rish
    inlines = [CRMLeadNotesInline, CRMActivityInline, CRMLeadLostInline]

    def status_tag(self, obj):
        colors = {
            'active': '#007bff',    # Moviy
            'converted': '#28a745', # Yashil
            'lost': '#dc3545',      # Qizil
        }
        color = colors.get(obj.status, 'grey')
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 10px; border-radius: 10px; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_tag.short_description = "Status"

    def source_tag(self, obj):
        if obj.source:
            return format_html('<small style="color: #666;">📢 {}</small>', obj.source.name)
        return "-"
    source_tag.short_description = "Manba"
#
# @admin.register(CRMPipelines)
# class CRMPipelinesAdmin(admin.ModelAdmin):
#     list_display = ['id', 'position', 'name'] # 'id' birinchi, 'position' endi tahrirlasa bo'ladi
#     list_editable = ['position']
#     list_display_links = ['id', 'name']
#
#     def get_leads_count(self, obj):
#         return obj.leads.count()
#     get_leads_count.short_description = "Lidlar soni"

@admin.register(CrmSection)
class CrmSectionAdmin(BaseModelAdmin):
    list_display = ('name', 'pipeline', 'course', 'teacher', 'time_info')
    list_filter = ('pipeline', 'course', 'teacher')
    search_fields = ('name',)

    def time_info(self, obj):
        if obj.days and obj.time:
            return f"{obj.days} | {obj.time}"
        return "-"
    time_info.short_description = "Vaqt/Kunlar"

@admin.register(CRMActivity)
class CRMActivityAdmin(admin.ModelAdmin):
    list_display = ('lead', 'activity_type_icon', 'result', 'created_by', 'created_at')
    list_filter = ('activity_type', 'created_at')
    search_fields = ('lead__full_name', 'result')

    def activity_type_icon(self, obj):
        icons = {
            'call': '📞 Qo\'ng\'iroq',
            'sms': '💬 SMS',
            'meeting': '🤝 Uchrashuv',
        }
        return icons.get(obj.activity_type, obj.activity_type)
    activity_type_icon.short_description = "Turi"

@admin.register(CRMLeadsHistory)
class CRMLeadsHistoryAdmin(admin.ModelAdmin):
    list_display = ('lead', 'old_pipeline', 'new_pipeline', 'changed_by', 'changed_at')
    readonly_fields = ('lead', 'old_pipeline', 'new_pipeline', 'changed_by', 'changed_at')

    def has_add_permission(self, request): return False # Tarix qo'shilmaydi

@admin.register(CRMSource, CRMLostReason)
class SimpleCrmAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(CRMLeadNotes)
class CRMLeadNotesAdmin(admin.ModelAdmin):
    list_display = ('lead', 'user', 'note_short', 'created_at')

    def note_short(self, obj):
        return obj.note[:50] + "..." if len(obj.note) > 50 else obj.note