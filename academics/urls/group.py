from django.urls import path, include
from rest_framework.routers import DefaultRouter

from academics.views.groups import GroupViewSet, RoomViewSet, CourseViewSet

router = DefaultRouter()

# Barcha CRUD amallari avtomatik generatsiya qilinadi
router.register(r'rooms', RoomViewSet, basename='room')
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'groups', GroupViewSet, basename='group')

urlpatterns = [
    path('', include(router.urls)),
]