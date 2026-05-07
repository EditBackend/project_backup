from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import TaskBoard, TaskColumn, Task, TaskComment, BoardPermission
from .serializers import (
    TaskBoardSerializer, TaskColumnSerializer, TaskSerializer,
    TaskCommentSerializer, BoardPermissionSerializer
)
# AuditLogMixin audit.mixins faylida turibdi deb faraz qilamiz
from audit.mixin import AuditLogMixin


class BaseTaskViewSet(AuditLogMixin, viewsets.ModelViewSet):
    """ Barcha Task ViewSet'lar uchun umumiy ota-klass """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.organization:
            return self.queryset.none()
        return self.queryset.filter(organization=user.organization).order_by('-created_at')

    def perform_create(self, serializer):
        # Frontenddan ishonmay, maktabni backendda majburan ulaymiz
        serializer.save(
            organization=self.request.user.organization,
            created_by=self.request.user
        )


# Doskalar
class TaskBoardViewSet(BaseTaskViewSet):
    queryset = TaskBoard.objects.all()
    serializer_class = TaskBoardSerializer


# Ustunlar
class TaskColumnViewSet(BaseTaskViewSet):
    queryset = TaskColumn.objects.all()
    serializer_class = TaskColumnSerializer

    def get_queryset(self):
        # Ustunlar yaratilgan vaqtiga emas, o'zining position (joylashuv) tartibida chiqishi kerak
        return super().get_queryset().order_by('position')


# Asosiy Vazifalar
class TaskViewSet(BaseTaskViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


# Izohlar
class TaskCommentViewSet(BaseTaskViewSet):
    queryset = TaskComment.objects.all()
    serializer_class = TaskCommentSerializer


# Ruxsatlar
class BoardPermissionViewSet(BaseTaskViewSet):
    queryset = BoardPermission.objects.all()
    serializer_class = BoardPermissionSerializer