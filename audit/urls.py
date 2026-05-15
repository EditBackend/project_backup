from django.urls import path
from .views import AuditLogViewSet

audit_list = AuditLogViewSet.as_view({'get': 'list'})
audit_detail = AuditLogViewSet.as_view({'get': 'retrieve'})

urlpatterns = [
    # Ro'yxatni ko'rish (Search va Filter bilan)
    path('audit-logs/', audit_list, name='audit-log-list'),
    
    # UUID orqali aniq bir logni ko'rish
    path('audit-logs/<uuid:pk>/', audit_detail, name='audit-log-detail'),
]