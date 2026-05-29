from django.urls import path
from .views import (
    PipelineViewSet as CRMPipelineViewSet,
    CRMSourceViewSet,
    CRMLeadViewSet,
    CRMActivityViewSet,
    CRMLeadLostViewSet,
    CRMLeadsHistoryViewSet,
    CrmSectionViewSet
)

urlpatterns = [
    # ====================== PIPELINES ======================
    path('pipelines/', CRMPipelineViewSet.as_view({'get': 'list', 'post': 'create'}), name='crm-pipeline-list'),
    path('pipelines/<uuid:pk>/', CRMPipelineViewSet.as_view({
        'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'
    }), name='crm-pipeline-detail'),

    # ====================== SOURCES ======================
    # 💡 DIQQAT: Frontend UUID yuborayotgani uchun <int:pk> ni <uuid:pk> ga o'zgartirdik!
    path('sources/', CRMSourceViewSet.as_view({'get': 'list', 'post': 'create'}), name='crm-source-list'),
    path('sources/<uuid:pk>/', CRMSourceViewSet.as_view({
        'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'
    }), name='crm-source-detail'),

    # ====================== HISTORY ======================
    path('history/', CRMLeadsHistoryViewSet.as_view({'get': 'list', 'post': 'create'}), name='crm-history-list'),
    path('history/<uuid:pk>/', CRMLeadsHistoryViewSet.as_view({
        'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'
    }), name='crm-history-detail'),

    # ====================== SECTIONS ======================
    path('sections/', CrmSectionViewSet.as_view({'get': 'list', 'post': 'create'}), name='crm-section-list'),
    path('sections/<uuid:pk>/', CrmSectionViewSet.as_view({
        'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'
    }), name='crm-section-detail'),

    # ====================== LEADS ======================
    path('leads/', CRMLeadViewSet.as_view({'get': 'list', 'post': 'create'}), name='crm-lead-list'),
    path('leads/<uuid:pk>/', CRMLeadViewSet.as_view({
        'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'
    }), name='crm-lead-detail'),

    # ====================== ACTIVITIES ======================
    path('activities/', CRMActivityViewSet.as_view({'get': 'list', 'post': 'create'}), name='crm-activity-list'),
    path('activities/<uuid:pk>/', CRMActivityViewSet.as_view({
        'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'
    }), name='crm-activity-detail'),

    # ====================== LOST LEADS ======================
    path('lost-leads/', CRMLeadLostViewSet.as_view({'get': 'list', 'post': 'create'}), name='crm-lost-lead-list'),
    path('lost-leads/<uuid:pk>/', CRMLeadLostViewSet.as_view({
        'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'
    }), name='crm-lost-lead-detail'),
]