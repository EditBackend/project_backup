from django.urls import path
from .views import (
    TariffPlanViewSet, OrganizationViewSet,
    BranchViewSet, SubscriptionViewSet,
    OrganizationLoginView 
)

urlpatterns = [
    # Login
    path('login/', OrganizationLoginView.as_view(), name='org-login'),

    # Organizations
    path('organizations/', OrganizationViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('organizations/<uuid:pk>/', OrganizationViewSet.as_view({
        'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'
    })),

    # Branches (UUID-ga o'tkazildi)
    path('branches/', BranchViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('branches/<uuid:pk>/', BranchViewSet.as_view({
        'get': 'retrieve', 'put': 'update', 'delete': 'destroy'
    })),

    # Tariffs & Subscriptions
    path('tariffs/', TariffPlanViewSet.as_view({'get': 'list'})),
    path('subscriptions/', SubscriptionViewSet.as_view({
        'get': 'list', 
        'post': 'create'  # Yangi obuna yaratish uchun
    })),
]