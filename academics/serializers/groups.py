from rest_framework import serializers
from django.db import transaction
from django.db.models import Q
from datetime import date
from accounts.models import Employee
from academics.models import Group, Course, Room, StudentGroup, GroupTeacher


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'name', 'capacity','organization']
        read_only_fields = ['id']


class CourseMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'name', 'monthly_price']


class GroupListSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course.name', read_only=True)
    room_name = serializers.CharField(source='room.name', read_only=True)
    student_count = serializers.IntegerField(read_only=True, default=0)
    teacher_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Group
        fields = [
            'id', 'name', 'course_name', 'room_name',
            'start_date', 'end_date', 'status',
            'teacher_count', 'student_count'
        ]


class GroupDetailSerializer(serializers.ModelSerializer):
    course = CourseMinimalSerializer()
    room = RoomSerializer()
    teachers = serializers.SerializerMethodField()
    students = serializers.SerializerMethodField()
    statistics = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = '__all__'

    def get_teachers(self, obj):
        teachers = obj.group_teachers.select_related('teacher__user').filter(end_date__isnull=True)
        return [{
            'id': str(t.teacher.id),
            'full_name': t.teacher.user.full_name if t.teacher.user else "Noma'lum",
            'start_date': t.start_date
        } for t in teachers]

    def get_students(self, obj):
        students = StudentGroup.objects.filter(group=obj, left_at__isnull=True).select_related('student')
        return [{
            'id': str(s.student.id),
            'full_name': s.student.full_name,
            'phone': s.student.phone_number,
            'joined_at': s.joined_at
        } for s in students]

    def get_statistics(self, obj):
        total_students = StudentGroup.objects.filter(group=obj).count()
        active_students = StudentGroup.objects.filter(group=obj, left_at__isnull=True).count()
        return {
            'total_students': total_students,
            'active_students': active_students,
            'left_students': total_students - active_students,
            'days_until_end': (obj.end_date - date.today()).days if obj.end_date else None,
        }


class GroupWriteSerializer(serializers.ModelSerializer):
    """ Faqat yaratish va tahrirlash uchun (Audit'siz, lekin qat'iy Validatsiyali) """
    teacher_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True, required=False
    )
    course_id = serializers.UUIDField(write_only=True)
    room_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Group
        fields = ['id', 'name', 'course_id', 'room_id', 'status', 'start_date', 'end_date', 'teacher_ids']

    def validate(self, attrs):
        request = self.context.get('request')
        org = request.user.organization if request else None

        # 1. Tashkilot xavfsizligi (IDOR oldini olish)
        course_id = attrs.get('course_id')
        if course_id and not Course.objects.filter(id=course_id, organization=org).exists():
            raise serializers.ValidationError({"course_id": "Kurs topilmadi yoki boshqa maktabga tegishli."})

        room_id = attrs.get('room_id')
        if room_id and not Room.objects.filter(id=room_id, organization=org).exists():
            raise serializers.ValidationError({"room_id": "Xona topilmadi yoki boshqa maktabga tegishli."})

        # 2. Sanalar mantiqi
        start_date = attrs.get('start_date', getattr(self.instance, 'start_date', None))
        end_date = attrs.get('end_date', getattr(self.instance, 'end_date', None))
        if start_date and end_date and start_date >= end_date:
            raise serializers.ValidationError(
                {'end_date': 'Tugash sanasi boshlanish sanasidan oldin bo\'lishi mumkin emas.'})

        # 3. Xona bandligi (O'zaro to'qnashuvni tekshirish)
        if room_id and start_date and end_date:
            overlapping = Group.objects.filter(room_id=room_id, status='active').filter(
                Q(start_date__lte=end_date) & Q(end_date__gte=start_date)
            )
            if self.instance:
                overlapping = overlapping.exclude(pk=self.instance.pk)
            if overlapping.exists():
                conflict = overlapping.first()
                raise serializers.ValidationError(
                    {'room_id': f'Bu xonada boshqa guruh ({conflict.name}) dars o\'tadi.'})

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        teacher_ids = validated_data.pop('teacher_ids', [])
        validated_data['course'] = Course.objects.get(id=validated_data.pop('course_id'))
        if validated_data.get('room_id'):
            validated_data['room'] = Room.objects.get(id=validated_data.pop('room_id'))

        group = Group.objects.create(**validated_data)

        if teacher_ids:
            self._assign_teachers(group, teacher_ids, group.start_date)

        return group

    @transaction.atomic
    def update(self, instance, validated_data):
        teacher_ids = validated_data.pop('teacher_ids', None)

        if 'course_id' in validated_data:
            instance.course = Course.objects.get(id=validated_data.pop('course_id'))
        if 'room_id' in validated_data:
            room_id = validated_data.pop('room_id')
            instance.room = Room.objects.get(id=room_id) if room_id else None

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if teacher_ids is not None:
            instance.group_teachers.filter(end_date__isnull=True).update(end_date=date.today())
            self._assign_teachers(instance, teacher_ids, date.today())

        return instance

    def _assign_teachers(self, group, teacher_ids, start_date):
        request = self.context.get('request')
        teachers = Employee.objects.filter(id__in=teacher_ids, user__organization=request.user.organization)
        if len(teachers) != len(teacher_ids):
            raise serializers.ValidationError(
                {'teacher_ids': 'Ba\'zi o\'qituvchilar topilmadi yoki boshqa maktabga tegishli.'})

        for teacher in teachers:
            GroupTeacher.objects.create(
                group=group, teacher=teacher, start_date=start_date,
                organization=request.user.organization, created_by=request.user
            )

    def to_representation(self, instance):
        return GroupDetailSerializer(instance, context=self.context).data

# Buni academics/serializers/groups.py faylining oxiriga qo'shing:
class GroupTeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupTeacher
        fields = '__all__'  # yoki o'zingizga kerakli maydonlar ro'yxati