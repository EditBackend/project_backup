from rest_framework import serializers
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import TaskBoard, TaskColumn, Task, TaskComment, BoardPermission

User = get_user_model()


class TaskBoardSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        error_messages={'blank': "Doska nomini kiritish majburiy."}
    )

    class Meta:
        model = TaskBoard
        fields = ['id', 'name', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']


class TaskColumnSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskColumn
        fields = ['id', 'board', 'name', 'position']

    def validate_board(self, value):
        request = self.context.get('request')
        if value.organization != request.user.organization:
            raise serializers.ValidationError("Tanlangan doska sizning tashkilotingizga tegishli emas.")
        return value


class TaskSerializer(serializers.ModelSerializer):
    title = serializers.CharField(
        required=True,
        error_messages={'blank': "Vazifa sarlavhasini kiritish majburiy."}
    )

    class Meta:
        model = Task
        fields = [
            'id', 'board', 'column', 'title', 'description',
            'assigned_to', 'deadline', 'priority', 'status', 'updated_at'
        ]
        read_only_fields = ['id', 'updated_at']

    def validate_deadline(self, value):
        if value and value < timezone.now():
            raise serializers.ValidationError(
                "Vazifa muddati (deadline) o'tgan vaqt bo'lishi mumkin emas. Iltimos, kelajakdagi sanani tanlang."
            )
        return value

    def validate_assigned_to(self, users):
        """ Biriktirilayotgan xodimlar haqiqatdan shu maktabdami? """
        request = self.context.get('request')
        for user in users:
            if user.organization != request.user.organization:
                raise serializers.ValidationError(
                    f"Xodim ({user.full_name}) sizning tashkilotingizda ishlamaydi. Boshqa maktab xodimiga vazifa bera olmaysiz."
                )
        return users

    def validate(self, attrs):
        request = self.context.get('request')
        board = attrs.get('board')
        column = attrs.get('column')

        # 1. Tashkilot xavfsizligi
        if board and board.organization != request.user.organization:
            raise serializers.ValidationError({"board": "Ushbu doska sizning maktabingizga tegishli emas."})

        # 2. Mantiqiy xavfsizlik: Tanlangan ustun haqiqatdan ham shu doskanikimi?
        if board and column and column.board != board:
            raise serializers.ValidationError({
                "column": f"'{column.name}' ustuni '{board.name}' doskasiga tegishli emas. Iltimos, to'g'ri ustunni tanlang."
            })

        return attrs


class TaskCommentSerializer(serializers.ModelSerializer):
    # Frontend uchun izoh qoldirgan odamning ismini qo'shib yuboramiz
    user_name = serializers.CharField(source='created_by.full_name', read_only=True)

    class Meta:
        model = TaskComment
        fields = ['id', 'task', 'comment', 'user_name', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_task(self, value):
        request = self.context.get('request')
        if value.organization != request.user.organization:
            raise serializers.ValidationError("Boshqa tashkilot vazifasiga izoh qoldira olmaysiz.")
        return value


class BoardPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoardPermission
        fields = ['id', 'board', 'user', 'can_create_tasks', 'can_edit_tasks', 'can_delete_tasks']

    def validate(self, attrs):
        request = self.context.get('request')
        board = attrs.get('board')
        user = attrs.get('user')

        if user.organization != request.user.organization:
            raise serializers.ValidationError({"user": "Faqat o'z xodimlaringizga ruxsat bera olasiz."})

        # Bitta odamga bitta doska uchun qayta-qayta ruxsat berilishini oldini olamiz
        if BoardPermission.objects.filter(board=board, user=user).exists():
            raise serializers.ValidationError({
                "user": "Ushbu xodimga bu doska uchun allaqachon ruxsat berilgan. Yangisini ochmasdan eskisini tahrirlang."
            })

        return attrs