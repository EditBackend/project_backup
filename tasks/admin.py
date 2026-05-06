# from django.contrib import admin
# from django.utils.html import format_html
# from django.utils import timezone
# from .models import (
#     TaskBoards, TaskColumns, Task, TaskComments,
#     TaskActivityLogs, TaskNotifications, TaskPermissions
# )
#
# # ==================== INLINES ====================
#
# class TaskColumnInline(admin.TabularInline):
#     model = TaskColumns
#     extra = 1
#     fields = ['name', 'position']
#     search_fields = ['name'] # BU SHART
#
# class TaskCommentInline(admin.StackedInline):
#     model = TaskComments
#     extra = 0
#     readonly_fields = ['created_at']
#
# class TaskActivityLogInline(admin.TabularInline):
#     model = TaskActivityLogs
#     extra = 0
#     readonly_fields = ['user', 'old_value', 'new_value', 'performed_by', 'created_at']
#     can_delete = False
#
# # ==================== ADMIN CLASSES ====================
#
# @admin.register(TaskBoards)
# class TaskBoardsAdmin(admin.ModelAdmin):
#     list_display = ('name', 'tasks_count', 'created_by', 'created_at')
#     search_fields = ('name',)
#     inlines = [TaskColumnInline]
#
#     def tasks_count(self, obj):
#         return obj.Task_board.count()
#     tasks_count.short_description = "Vazifalar soni"
#
# @admin.register(Task)
# class TaskAdmin(admin.ModelAdmin):
#     list_display = (
#         'title_short', 'board', 'column_tag',
#         'assigned_to', 'priority_badge', 'deadline_status', 'status'
#     )
#     list_filter = ('board', 'priority', 'status', 'deadline')
#     search_fields = ('title', 'description', 'assigned_to__user__first_name')
#     autocomplete_fields = ['assigned_to', 'board', 'column']
#     inlines = [TaskCommentInline, TaskActivityLogInline]
#
#     def title_short(self, obj):
#         return obj.title[:50] + "..." if len(obj.title) > 50 else obj.title
#     title_short.short_description = "Vazifa"
#
#     def column_tag(self, obj):
#         return format_html('<span style="color: #666; font-style: italic;">📁 {}</span>', obj.column.name)
#     column_tag.short_description = "Ustun"
#
#     def priority_badge(self, obj):
#         colors = {
#             'low': '#28a745',    # Yashil
#             'medium': '#17a2b8', # Moviy
#             'high': '#fd7e14',   # To'q sariq
#             'urgent': '#dc3545'  # Qizil
#         }
#         return format_html(
#             '<span style="background: {}; color: white; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 10px; text-transform: uppercase;">{}</span>',
#             colors.get(obj.priority, 'grey'), obj.get_priority_display()
#         )
#     priority_badge.short_description = "Prioritet"
#
#     def deadline_status(self, obj):
#         if obj.deadline < timezone.now() and obj.status != 'completed':
#             return format_html('<b style="color: #dc3545;">⏰ O\'tib ketgan ({})</b>', obj.deadline.strftime("%d.%m"))
#         return obj.deadline.strftime("%d.%m.%Y %H:%M")
#     deadline_status.short_description = "Deadline"
#
# @admin.register(TaskActivityLogs)
# class TaskActivityLogsAdmin(admin.ModelAdmin):
#     list_display = ('task', 'performed_by', 'created_at')
#     list_filter = ('created_at', 'performed_by')
#     readonly_fields = ('task', 'user', 'old_value', 'new_value', 'performed_by', 'created_at')
#
#     def has_add_permission(self, request): return False
#
# @admin.register(TaskNotifications)
# class TaskNotificationsAdmin(admin.ModelAdmin):
#     list_display = ('task', 'user', 'notify_at', 'status_icon')
#
#     def status_icon(self, obj):
#         return format_html('✅ Yuborildi' if obj.is_sent else '⏳ Kutilmoqda')
#     status_icon.short_description = "Holat"
#
# # Oddiyroq modullarni ro'yxatga olish
# @admin.register(TaskColumns)
# class TaskColumnsAdmin(admin.ModelAdmin):
#     list_display = ('id', 'name', 'board')
#     search_fields = ('name',) # BU YERDA SHART!
#
#
#
# admin.site.register(TaskComments)
# admin.site.register(TaskPermissions)