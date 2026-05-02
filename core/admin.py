from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone

class BaseModelAdmin(admin.ModelAdmin):
    """
    Barcha admin classlar uchun universal poydevor.
    Bu klass meros olinganda avtomatik ravishda:
    1. created_at/updated_at ni ro'yxatga qo'shadi.
    2. Readonly maydonlarni boshqaradi.
    3. Userni (Employee) avtomatik biriktiradi.
    """

    # Umumiy interfeys sozlamalari
    list_per_page = 20
    save_on_top = True
    show_full_result_count = True
    
    # Ro'yxatni chiroyli ko'rsatish
    def get_list_display(self, request):
        list_display = list(super().get_list_display(request))
        fields = [f.name for f in self.model._meta.fields]
        
        # Avtomatik ravishda muhim maydonlarni oxiriga qo'shish
        if 'status' in fields and 'status' not in list_display:
            list_display.append('status_badge')
        if 'created_at' in fields and 'created_at' not in list_display:
            list_display.append('formatted_created_at')
        
        return list_display

    # Tahrirlab bo'lmaydigan maydonlar
    def get_readonly_fields(self, request, obj=None):
        readonly = list(super().get_readonly_fields(request, obj))
        universal_readonly = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']
        
        fields = [f.name for f in self.model._meta.fields]
        for field in universal_readonly:
            if field in fields and field not in readonly:
                readonly.append(field)
        return readonly

    # --- VIZUAL METODLAR ---

    def status_badge(self, obj):
        if not hasattr(obj, 'status'):
            return "-"
        
        colors = {
            'active': '#28a745',   # Yashil
            'inactive': '#dc3545', # Qizil
            'pending': '#ffc107',  # Sariq
            'frozen': '#17a2b8',   # Moviy
            'graduated': '#6f42c1' # Siyohrang
        }
        color = colors.get(obj.status, '#6c757d') # Default kulrang
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 12px; '
            'border-radius: 12px; font-weight: bold; font-size: 11px;">{}</span>',
            color, obj.get_status_display().upper() if hasattr(obj, 'get_status_display') else obj.status.upper()
        )
    status_badge.short_description = 'Status'

    def formatted_created_at(self, obj):
        if not obj.created_at:
            return "-"
        # Bugun yaratilgan bo'lsa faqat soatni, aks holda sanani ko'rsatadi
        now = timezone.now()
        if obj.created_at.date() == now.date():
            return format_html('<b style="color: #007bff;">Bugun, {}</b>', obj.created_at.strftime("%H:%M"))
        return obj.created_at.strftime("%d.%m.%Y")
    formatted_created_at.short_description = 'Yaratildi'

    # --- AVTOMATIK MA'LUMOT TO'LDIRISH ---

    def save_model(self, request, obj, form, change):
        # request.user bu User modeli, bizga esa Employee kerak
        employee = getattr(request.user, 'employee', None)
        
        if not change: # Yangi yaratilayotgan bo'lsa
            if hasattr(obj, 'created_by'):
                obj.created_by = employee
            # Agar modelda organization/branch bo'lsa va userda ham bo'lsa, avtomatik to'ldiramiz
            if hasattr(obj, 'organization') and not obj.organization:
                obj.organization = request.user.organization
            if hasattr(obj, 'branch') and not obj.branch:
                obj.branch = request.user.branch
        
        if hasattr(obj, 'updated_by'):
            obj.updated_by = employee
            
        super().save_model(request, obj, form, change)