from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CRMPipelineViewSet, CRMSourceViewSet,
    CRMLeadViewSet, CRMActivityViewSet, CRMLeadLostViewSet
)

router = DefaultRouter()

# Lug'atlar
router.register(r'crm/pipelines', CRMPipelineViewSet, basename='crm-pipeline')
router.register(r'crm/sources', CRMSourceViewSet, basename='crm-source')

# Asosiy CRM
router.register(r'crm/leads', CRMLeadViewSet, basename='crm-lead')
router.register(r'crm/activities', CRMActivityViewSet, basename='crm-activity')
router.register(r'crm/lost-leads', CRMLeadLostViewSet, basename='crm-lost-lead')

urlpatterns = [
    path('', include(router.urls)),
]