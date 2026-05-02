from django.urls import path
from .views import (
    UserViewSet, EmployeeViewSet, RoleViewSet,
    RolePermissionViewSet, UserRoleViewSet
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import registration_view
urlpatterns = [
    # User URLs
    # Ro'yxatdan o'tish (Ariza topshirish)
    path('register/', registration_view, name='register'),

    # Login qilish (Token olish)
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('users/', UserViewSet.as_view({'get': 'list', 'post': 'create'}), name='user-list'),
    path('users/<int:pk>/',
         UserViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}),
         name='user-detail'),

    # Employee URLs
    path('employees/', EmployeeViewSet.as_view({'get': 'list', 'post': 'create'}), name='employee-list'),
    path('employees/<uuid:pk>/',
         EmployeeViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}),
         name='employee-detail'),

    # Role URLs
    path('roles/', RoleViewSet.as_view({'get': 'list', 'post': 'create'}), name='role-list'),
    path('roles/<int:pk>/',
         RoleViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}),
         name='role-detail'),

    # RolePermission URLs
    path('role-permissions/', RolePermissionViewSet.as_view({'get': 'list', 'post': 'create'}),
         name='rolepermission-list'),
    path('role-permissions/<int:pk>/', RolePermissionViewSet.as_view(
        {'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}),
         name='rolepermission-detail'),

    # UserRole URLs
    path('user-roles/', UserRoleViewSet.as_view({'get': 'list', 'post': 'create'}), name='userrole-list'),
    path('user-roles/<int:pk>/',
         UserRoleViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}),
         name='userrole-detail'),
]