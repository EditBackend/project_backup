from django.urls import path
from .views import (
    SmsTemplatesViewSet,
    SmsSchedulesViewSet,
    SMSMessagesViewSet, 
    SmsProviderViewSet
)

urlpatterns = [
    # Templates
    path('sms-templates/', SmsTemplatesViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('sms-templates/<uuid:pk>/', SmsTemplatesViewSet.as_view({
        'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'
    })),

    # Schedules
    path('sms-schedules/', SmsSchedulesViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('sms-schedules/<uuid:pk>/', SmsSchedulesViewSet.as_view({
        'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'
    })),

    # Messages
    path('sms-messages/', SMSMessagesViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('sms-messages/<uuid:pk>/', SMSMessagesViewSet.as_view({
        'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'
    })),

    # Providers
    path('providers/', SmsProviderViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('providers/<uuid:pk>/', SmsProviderViewSet.as_view({
        'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'
    })),
]