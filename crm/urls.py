from django.urls import path
from .views import (
    CRMSourceViewSet,
    CRMPipelinesViewSet,
    CRMLeadViewSet,
    CRMActivityViewSet,
    CRMLeadsHistoryViewSet,
    CRMLostReasonViewSet,
    CRMLeadLostViewSet,
    CRMLeadNotesViewSet,
    CrmSectionViewSet,
    LeadFormViewSet

)


urlpatterns = [
    # Lead Formalar ro'yxati va yaratish
    path('lead-forms/',
         LeadFormViewSet.as_view({'get': 'list', 'post': 'create'}),
         name='leadform-list'),

    # Bitta forma detallari, o'zgartirish, o'chirish
    path('lead-forms/<int:pk>/',
         LeadFormViewSet.as_view({
             'get': 'retrieve',
             'put': 'update',
             'patch': 'partial_update',
             'delete': 'destroy'
         }),
         name='leadform-detail'),

    # Qo'shimcha amallar
    path('lead-forms/<int:pk>/duplicate/',
         LeadFormViewSet.as_view({'post': 'duplicate'}),
         name='leadform-duplicate'),

    path('lead-forms/field-types/',
         LeadFormViewSet.as_view({'get': 'field_types'}),
         name='leadform-field-types'),
    path('crm-sections/', CrmSectionViewSet.as_view({'get': 'list', 'post': 'create'}), name='crmsections-list'),
    path('crm-sections/<uuid:pk>/', CrmSectionViewSet.as_view({
        'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'
    }), name='crmsections-detail'),

    path('crm-sources/', CRMSourceViewSet.as_view({'get': 'list', 'post': 'create'}), name='crmsource-list'),
    path('crm-sources/<uuid:pk>/', CRMSourceViewSet.as_view({
        'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'
    }), name='crmsource-detail'),


    path('crm-pipelines/', CRMPipelinesViewSet.as_view({'get': 'list', 'post': 'create'}), name='crmpipeline-list'),
    path('crm-pipelines/<uuid:pk>/', CRMPipelinesViewSet.as_view({
        'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'
    }), name='crmpipeline-detail'),


    path('crm-leads/', CRMLeadViewSet.as_view({'get': 'list', 'post': 'create'}), name='crmlead-list'),
    path('crm-leads/<uuid:pk>/', CRMLeadViewSet.as_view({
        'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'
    }), name='crmlead-detail'),


    path('crm-activities/', CRMActivityViewSet.as_view({'get': 'list', 'post': 'create'}), name='crmactivity-list'),
    path('crm-activities/<uuid:pk>/', CRMActivityViewSet.as_view({
        'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'
    }), name='crmactivity-detail'),


    path('crm-leads-history/', CRMLeadsHistoryViewSet.as_view({'get': 'list', 'post': 'create'}), name='crmleadshistory-list'),
    path('crm-leads-history/<uuid:pk>/', CRMLeadsHistoryViewSet.as_view({
        'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'
    }), name='crmleadshistory-detail'),


    path('crm-lost-reasons/', CRMLostReasonViewSet.as_view({'get': 'list', 'post': 'create'}), name='crmlostreason-list'),
    path('crm-lost-reasons/<uuid:pk>/', CRMLostReasonViewSet.as_view({
        'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'
    }), name='crmlostreason-detail'),


    path('crm-lead-lost/', CRMLeadLostViewSet.as_view({'get': 'list', 'post': 'create'}), name='crmleadlost-list'),
    path('crm-lead-lost/<uuid:pk>/', CRMLeadLostViewSet.as_view({
        'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'
    }), name='crmleadlost-detail'),


    path('crm-lead-notes/', CRMLeadNotesViewSet.as_view({'get': 'list', 'post': 'create'}), name='crmleadnotes-list'),
    path('crm-lead-notes/<uuid:pk>/', CRMLeadNotesViewSet.as_view({
        'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'
    }), name='crmleadnotes-detail'),
]
