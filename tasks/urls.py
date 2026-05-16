from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import (
    TaskBoardViewSet, TaskColumnViewSet, TaskViewSet,
    TaskCommentViewSet, BoardPermissionViewSet
)

router = SimpleRouter()

router.register(r'tasks/boards', TaskBoardViewSet, basename='task-board')
router.register(r'tasks/columns', TaskColumnViewSet, basename='task-column')
router.register(r'tasks/items', TaskViewSet, basename='task-item')
router.register(r'tasks/comments', TaskCommentViewSet, basename='task-comment')
router.register(r'tasks/permissions', BoardPermissionViewSet, basename='task-permission')

urlpatterns = [
    path('', include(router.urls)),
]