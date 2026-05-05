from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import registration_view, EmployeeViewSet

# 1. DRF Router yaratamiz
router = DefaultRouter()

# 2. ViewSet'larni ulash (avtomat barcha CRUD yo'llarini yaratadi)
router.register(r'employees', EmployeeViewSet, basename='employee')

# 3. Asosiy URL ro'yxati
urlpatterns = [
    # ─── AVTORIZATSIYA (AUTH) ─────────────────────────
    # Ro'yxatdan o'tish (Superadmin va yangi tashkilot)
    path('register/', registration_view, name='register'),

    # Login qilish va Token olish (Hamma uchun yagona)
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),

    # Tokenni yangilash (Access token eskirganda Refresh orqali yangisini olish)
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # ─── ASOSIY API YO'LLARI (ROUTER) ─────────────────
    # Bunga /employees/ va /employees/<id>/ avtomatik kiradi
    path('', include(router.urls)),
]