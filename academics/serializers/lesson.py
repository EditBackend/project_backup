from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta
from academics.models import (
    LessonSchedule, Attendence, Exams, ExamResults, OnlineLesson, Group
)


class LessonScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonSchedule
        fields = ['id', 'group', 'day_type', 'start_time', 'end_time']
        read_only_fields = ['id']

    def validate(self, attrs):
        if attrs['start_time'] >= attrs['end_time']:
            raise serializers.ValidationError(
                {"end_time": "Darsning tugash vaqti boshlanish vaqtidan keyin bo'lishi kerak."})
        return attrs


class LessonScheduleListSerializer(serializers.ModelSerializer):
    group_name = serializers.CharField(source='group.name', read_only=True)
    day_type_display = serializers.CharField(source='get_day_type_display', read_only=True)
    duration_minutes = serializers.SerializerMethodField()

    class Meta:
        model = LessonSchedule
        fields = [
            'id', 'group', 'group_name', 'day_type', 'day_type_display',
            'start_time', 'end_time', 'duration_minutes'
        ]

    def get_duration_minutes(self, obj):
        from datetime import datetime, date
        start = datetime.combine(date.today(), obj.start_time)
        end = datetime.combine(date.today(), obj.end_time)
        return (end - start).seconds // 60


class AttendenceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student_group.student.full_name', read_only=True)

    class Meta:
        model = Attendence
        fields = ['id', 'student_group', 'student_name', 'lesson_date', 'is_present', 'marked_by']
        read_only_fields = ['id', 'marked_by']

    def validate_lesson_date(self, value):
        today = timezone.now().date()
        if value < today - timedelta(days=3) or value > today:
            raise serializers.ValidationError("Davomatni faqat bugun yoki oxirgi 3 kun uchun kiritish mumkin.")
        return value


class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exams
        fields = ['id', 'group', 'title', 'exam_date', 'min_score', 'max_score', 'description', 'file']
        read_only_fields = ['id']

    def validate(self, attrs):
        if attrs.get('min_score') >= attrs.get('max_score'):
            raise serializers.ValidationError({"max_score": "Maksimal ball o'tish balidan yuqori bo'lishi shart."})
        return attrs


class ExamResultSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)

    class Meta:
        model = ExamResults
        fields = ['id', 'exam', 'student', 'student_name', 'score', 'comment']
        read_only_fields = ['id']


class OnlineLessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = OnlineLesson
        fields = '__all__'
        read_only_fields = ['id', 'is_published']