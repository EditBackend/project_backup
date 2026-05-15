from django.urls import path
from .views import (
    CRMPipelineViewSet, CRMSourceViewSet,
    CRMLeadViewSet, CRMActivityViewSet, CRMLeadLostViewSet,CRMLeadsHistoryViewSet,CrmSectionViewSet
)

urlpatterns = [
    # ====================== PIPELINES ======================
    path('crm/pipelines/', CRMPipelineViewSet.as_view({'get': 'list', 'post': 'create'}), name='crm-pipeline-list'),
    path('crm/pipelines/<int:pk>/', CRMPipelineViewSet.as_view({
        'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'
    }), name='crm-pipeline-detail'),

    # ====================== SOURCES ======================
    path('crm/sources/', CRMSourceViewSet.as_view({'get': 'list', 'post': 'create'}), name='crm-source-list'),
    path('crm/sources/<int:pk>/', CRMSourceViewSet.as_view({
        'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'
    }), name='crm-source-detail'),
    path('crm/history/', CRMLeadsHistoryViewSet.as_view({'get': 'list', 'post': 'create'}), name='crm-history-list'),
    path('crm/history/<int:pk>/', CRMLeadsHistoryViewSet.as_view({
        'get': 'retrieve',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='crm-history-detail'),
    path('crm/sections/', CrmSectionViewSet.as_view({'get': 'list', 'post': 'create'}), name='crm-section-list'),
    path('crm/sections/<uuid:pk>/', CrmSectionViewSet.as_view({
        'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'
    }), name='crm-section-detail'),

    # ====================== LEADS ======================
    path('crm/leads/', CRMLeadViewSet.as_view({'get': 'list', 'post': 'create'}), name='crm-lead-list'),
    path('crm/leads/<int:pk>/', CRMLeadViewSet.as_view({
        'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'
    }), name='crm-lead-detail'),

    # ====================== ACTIVITIES ======================
    path('crm/activities/', CRMActivityViewSet.as_view({'get': 'list', 'post': 'create'}), name='crm-activity-list'),
    path('crm/activities/<int:pk>/', CRMActivityViewSet.as_view({
        'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'
    }), name='crm-activity-detail'),

    # ====================== LOST LEADS ======================
    path('crm/lost-leads/', CRMLeadLostViewSet.as_view({'get': 'list', 'post': 'create'}), name='crm-lost-lead-list'),
    path('crm/lost-leads/<int:pk>/', CRMLeadLostViewSet.as_view({
        'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'
    }), name='crm-lost-lead-detail'),
]