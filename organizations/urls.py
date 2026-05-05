from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TariffPlanViewSet, OrganizationViewSet,
    BranchViewSet, SubscriptionViewSet
)

router = DefaultRouter()
router.register(r'tariffs', TariffPlanViewSet, basename='tariff')
router.register(r'organizations', OrganizationViewSet, basename='organization')
router.register(r'branches', BranchViewSet, basename='branch')
router.register(r'subscriptions', SubscriptionViewSet, basename='subscription')

urlpatterns = [
    path('', include(router.urls)),
]