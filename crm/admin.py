from django.contrib import admin
from django.utils.html import format_html
from .models import (
    CRMPipeline, CrmSection, CRMSource,
    CRMLead, CRMActivity, CRMLeadsHistory, CRMLostReason,
    CRMLeadLost, CRMLeadNotes
)
from core.admin import BaseModelAdmin


# ==================== INLINES ====================

class CRMActivityInline(admin.TabularInline):
    model = CRMActivity
    extra = 0
    # BaseModel'dagi created_at va created_by ishlatiladi
    readonly_fields = ['created_at', 'created_by']
    can_delete = False


class CRMLeadNotesInline(admin.StackedInline):
    model = CRMLeadNotes
    extra = 0
    # 'user' o'rniga BaseModel'dagi 'created_by' ishlatiladi
    fields = ['created_by', 'note']
    readonly_fields = ['created_by']


class CRMLeadLostInline(admin.TabularInline):
    model = CRMLeadLost
    extra = 0


# ==================== CRM ADMINS ====================

@admin.register(CRMPipeline)
class CRMPipelineAdmin(admin.ModelAdmin):
    list_display = ['id', 'position', 'name', 'get_leads_count']
    list_editable = ['position']

    def get_leads_count(self, obj):
        return obj.leads.count()

    get_leads_count.short_description = "Lidlar soni"


@admin.register(CRMLead)
class CRMLeadAdmin(BaseModelAdmin):
    # 'pipline' so'zi 'pipeline'ga to'g'rilandi
    list_display = (
        'full_name', 'phone_number', 'status_tag',
        'pipeline', 'assigned_to', 'source_tag', 'formatted_created_at'
    )
    list_filter = ('status', 'pipeline', 'source', 'branch', 'assigned_to')
    search_fields = ('full_name', 'phone_number')
    autocomplete_fields = ['assigned_to', 'section']

    inlines = [CRMLeadNotesInline, CRMActivityInline, CRMLeadLostInline]

    def status_tag(self, obj):
        colors = {
            'active': '#007bff',
            'converted': '#28a745',
            'lost': '#dc3545',
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
class CRMActivityAdmin(BaseModelAdmin):
    list_display = ('lead', 'activity_type_icon', 'result', 'created_by', 'created_at')
    list_filter = ('activity_type', 'created_at')
    search_fields = ('lead__full_name', 'result')

    def activity_type_icon(self, obj):
        icons = {'call': '📞 Qo\'ng\'iroq', 'sms': '💬 SMS', 'meeting': '🤝 Uchrashuv'}
        return icons.get(obj.activity_type, obj.activity_type)

    activity_type_icon.short_description = "Turi"


@admin.register(CRMLeadsHistory)
class CRMLeadsHistoryAdmin(admin.ModelAdmin):
    # 'changed_by' -> 'created_by', 'changed_at' -> 'created_at' ga almashtirildi
    list_display = ('lead', 'old_pipeline', 'new_pipeline', 'created_by', 'created_at')
    readonly_fields = ('lead', 'old_pipeline', 'new_pipeline', 'created_by', 'created_at')

    def has_add_permission(self, request): return False


@admin.register(CRMSource, CRMLostReason)
class SimpleCrmAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(CRMLeadNotes)
class CRMLeadNotesAdmin(admin.ModelAdmin):
    list_display = ('lead', 'created_by', 'note_short', 'created_at')

    def note_short(self, obj):
        return obj.note[:50] + "..." if len(obj.note) > 50 else obj.note

    note_short.short_description = "Eslatma"