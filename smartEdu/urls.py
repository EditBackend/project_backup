"""
URL configuration for smartEdu project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import github_webhook

# Spectacular (Swagger)
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

# JWT
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
# Swagger va Token uchun ruxsat
from rest_framework.permissions import AllowAny


urlpatterns = [
    # ====================== TOKEN OLISH (RUHSAT OCHILDI) ======================
    path(
        'api/token/',
        TokenObtainPairView.as_view(
            permission_classes=[AllowAny],     # ✅ Global xavfsizlik o'chirildi
            authentication_classes=[]          # ✅ Token so'ramasligi ta'minlandi
        ),
        name='token_obtain_pair'
    ),
    path(
        'api/token/refresh/',
        TokenRefreshView.as_view(
            permission_classes=[AllowAny],     # ✅ Global xavfsizlik o'chirildi
            authentication_classes=[]          # ✅ Token so'ramasligi ta'minlandi
        ),
        name='token_refresh'
    ),
    # =========================================================================

    path('admin/', admin.site.urls),

    # ====================== SWAGGER / SCHEMA ======================
    # OpenAPI Schema (JSON)
    path(
        "api/schema/",
        SpectacularAPIView.as_view(
            permission_classes=[AllowAny],
            authentication_classes=[],
        ),
        name="schema",
    ),

    # Swagger UI
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(
            url_name="schema",
            permission_classes=[AllowAny],
            authentication_classes=[],
        ),
        name="swagger-ui",
    ),

    # Redoc UI
    path(
        "api/redoc/",
        SpectacularRedocView.as_view(
            url_name="schema",
            permission_classes=[AllowAny],
            authentication_classes=[],
        ),
        name="redoc",
    ),
    # ====================== SWAGGER / SCHEMA ======================

    # App url'lari
    path('api/v1/academics/', include("academics.urls")),
    path('api/v1/accounts/', include("accounts.urls")),
    path('api/v1/audit/', include("audit.urls")),
    path('api/v1/communication/', include("communication.urls")),
    path('api/v1/crm/', include('crm.urls')),  # Bu yerda bitta crm/ bo'lishi kifoya
    path('api/v1/finance/', include("finance.urls")),
    path('api/v1/organizations/', include("organizations.urls")),
    path('api/v1/tasks/', include("tasks.urls")),
    path('api/v1/update-server-secret-url-99000/', github_webhook, name='update_server')
]

# Static va Media fayllar (DEBUG rejimida)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)