# from rest_framework import serializers
# from .models import ( LeaveReason, StudentGroupLeaves,
#     StudentFreezes, StudentBalanceHistory,
#     LessonTime,
#     TeacherSalaryRules, TeacherSalaryPayments, TeacherSalaryCalculations
# )
# from django.db import transaction
# from decimal import Decimal
# from django.utils import timezone
# from .models import StudentGroup, Student, StudentFreezes, Attendence
# from accounts.models import Employee
# from audit.models import AuditLog, AuditEntityType, AuditAction
# from .models import Student, StudentGroup, StudentFreezes
# from django.utils import timezone
# from django.db.models import Q
# from datetime import datetime
# from datetime import date
#
#
# from .models import (
#     StudentBalances, StudentTransaction
# )
# from rest_framework import serializers
# from .models import (
#     Group, GroupTeacher, Course, Room, LessonSchedule,
#     Student, StudentGroup, StudentPricing, Attendance, Exams, ExamResults
# )
# from audit.serializers import AuditLogSerializer
#
#
# # ==================== STUDENT SERIALIZERS ====================
# class StudentSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Student
#         fields = '__all__'
#
#
#
#
#
# class StudentPricingSerializer(serializers.ModelSerializer):
#     student_name = serializers.CharField(source='student.full_name', read_only=True)
#     course_name = serializers.CharField(source='course.name', read_only=True)
#     class Meta:
#         model = StudentPricing
#         fields = '__all__'
#
#
# class StudentBalancesSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = StudentBalances
#         fields = '__all__'
#
#
# class StudentTarnsactionsSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = StudentTarnsactions
#         fields = '__all__'
#
#     def create(self, validated_data):
#         with transaction.atomic():
#             # 1. To'lov amalini bazaga yozamiz
#             transaction_obj = super().create(validated_data)
#
#             # 2. Agar tranzaksiya turi "payment" bo'lsa balansni o'zgartiramiz
#             if transaction_obj.transaction_type == 'payment':
#                 balance_obj, _ = StudentBalances.objects.get_or_create(
#                     student=transaction_obj.student,
#                     branch=transaction_obj.branch,
#                     organization=transaction_obj.organization
#                 )
#                 # Matematik qoida: -300 + 250 = -50 (avtomatik qarzni yopadi)
#                 balance_obj.balance += transaction_obj.amount
#                 balance_obj.save()
#
#             return transaction_obj
#
#
# class LeaveReasonSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = LeaveReason
#         fields = '__all__'
#
#
# class StudentGroupLeavesSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = StudentGroupLeaves
#         fields = '__all__'
#         depth = 1
#
#
# class StudentFreezesSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = StudentFreezes
#         fields = '__all__'
#
#
# class StudentBalanceHistorySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = StudentBalanceHistory
#         fields = '__all__'
#
#
#
#
# from decimal import Decimal
# from django.db import transaction
# from django.utils import timezone
#
# class AttendenceSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Attendence
#         fields = ['id', 'student_group', 'lesson_date', 'is_present', 'marked_by']
#         extra_kwargs = {
#             'marked_by': {'required': False, 'allow_null': True}
#         }
#
#     def create(self, validated_data):
#         student_group = validated_data.get('student_group')
#         lesson_date = validated_data.get('lesson_date')
#         is_present = validated_data.get('is_present', False)
#         marked_by = validated_data.get('marked_by')
#
#         with transaction.atomic():
#
#             # ✅ 1. Attendence yaratish (Django o‘zi hammasini qiladi)
#             attendance = Attendence.objects.create(
#                 student_group=student_group,
#                 lesson_date=lesson_date,
#                 is_present=is_present,
#                 marked_by=marked_by
#             )
#
#             # ✅ 2. PUL YECHISH
#             if is_present:
#                 student = student_group.student
#                 course = getattr(student_group.group, 'course', None)
#
#                 if course:
#                     pricing = StudentPricing.objects.filter(
#                         student=student,
#                         course=course,
#                         start_date__lte=lesson_date,
#                         end_date__gte=lesson_date
#                     ).first()
#
#                     monthly_price = pricing.price_override if pricing else course.monthly_price
#                     lessons_count = Decimal(course.lesson_month) if course.lesson_month and course.lesson_month > 0 else Decimal(12)
#
#                     one_lesson_price = Decimal(monthly_price) / lessons_count
#
#                     # ✅ 3. Balans (branch muammosiz!)
#                     balance_obj, _ = StudentBalances.objects.get_or_create(
#                         student=student,
#                         defaults={'balance': Decimal('0')}
#                     )
#
#                     balance_obj.balance -= one_lesson_price
#                     balance_obj.save()
#
#                     # ✅ 4. History
#                     StudentBalanceHistory.objects.create(
#                         student=student,
#                         amount=-one_lesson_price,
#                         base_price=course.monthly_price,
#                         applied_price=one_lesson_price,
#                         discount=(course.monthly_price - monthly_price) if pricing else 0
#                     )
#
#             return attendance
#
#
#
#
# class GroupSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Group
#         fields = '__all__'
#
#
#
#
#
# # ==================== LESSON SERIALIZERS ====================
# class LessonTimeSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = LessonTime
#         fields = '__all__'
#
#
# class LessonScheduleSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = LessonSchedule
#         fields = '__all__'
#
#
# class ExamsSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Exams
#         fields = '__all__'
#
#
# class ExamResultsSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ExamResults
#         fields = '__all__'
#
#
#
#
# # ==================== TEACHER SERIALIZERS ====================
# class TeacherSalaryRulesSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TeacherSalaryRules
#         fields = '__all__'
#
#
# class TeacherSalaryPaymentsSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TeacherSalaryPayments
#         fields = '__all__'
#
#
# class TeacherSalaryCalculationsSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TeacherSalaryCalculations
#         fields = '__all__'
#
#
#
#
#
# class RoomSerializer(serializers.ModelSerializer):
#     """Xona uchun serializer"""
#
#     class Meta:
#         model = Room
#         fields = '__all__'
#         read_only_fields = ['id', 'created_at', 'updated_at']
#
#
# class CourseSerializer(serializers.ModelSerializer):
#     """Kurs uchun serializer"""
#     lesson_time = serializers.CharField(source='lesson.name', read_only=True)
#
#     class Meta:
#         model = Course
#         fields ='__all__'
#         read_only_fields = ['id', 'created_at', 'updated_at']
#
#
# class EmployeeSimpleSerializer(serializers.ModelSerializer):
#     """O'qituvchi uchun sodda serializer"""
#     full_name = serializers.SerializerMethodField()
#
#     class Meta:
#         model = Employee
#         fields = '__all__'
#
#     def get_full_name(self, obj):
#         return f"{obj.first_name} {obj.last_name}" if hasattr(obj, 'first_name') else str(obj)
#
#
# class GroupTeacherSerializer(serializers.ModelSerializer):
#     """Guruh o'qituvchisi uchun serializer"""
#     teacher_info = EmployeeSimpleSerializer(source='teacher', read_only=True)
#     group_name = serializers.CharField(source='group.name', read_only=True)
#
#     class Meta:
#         model = GroupTeacher
#         fields = '__all__'
#         read_only_fields = ['id', 'created_at', 'updated_at']
#
#     def validate(self, attrs):
#         """Validatsiyalar"""
#         start_date = attrs.get('start_date')
#         end_date = attrs.get('end_date')
#         group = attrs.get('group')
#         teacher = attrs.get('teacher')
#
#         # 1. Start date end date dan kichik bo'lishi kerak
#         if start_date and end_date:
#             if start_date >= end_date:
#                 raise serializers.ValidationError({
#                     'end_date': 'Tugash sanasi boshlanish sanasidan katta bolishi kerak.'
#                 })
#
#         # 2. O'qituvchi vaqti guruh davri ichida bo'lishi kerak
#         if group and start_date and end_date:
#             if start_date < group.start_date:
#                 raise serializers.ValidationError({
#                     'start_date': f'O\'qituvchi boshlanish sanasi guruh boshlanish sanasidan ({group.start_date}) oldin bo\'lmasligi kerak.'
#                 })
#             if end_date > group.end_date:
#                 raise serializers.ValidationError({
#                     'end_date': f'O\'qituvchi tugash sanasi guruh tugash sanasidan ({group.end_date}) keyin bo\'lmasligi kerak.'
#                 })
#
#         # 3. Bir o'qituvchi bir vaqtda ikki guruhda bo'lmasligi kerak (bir xil dars vaqtida)
#         if teacher and start_date and end_date and group and group.course and group.course.lesson:
#             conflicting = GroupTeacher.objects.filter(
#                 teacher=teacher,
#                 group__course__lesson=group.course.lesson,
#                 group__status='active'
#             ).filter(
#                 Q(start_date__lte=end_date) &
#                 Q(end_date__gte=start_date)
#             )
#
#             # Update qilayotgan bo'lsa, o'zini exclude qilish
#             if self.instance:
#                 conflicting = conflicting.exclude(pk=self.instance.pk)
#
#             if conflicting.exists():
#                 conflict = conflicting.first()
#                 raise serializers.ValidationError({
#                     'teacher': f'Bu o\'qituvchi shu vaqtda ({group.course.lesson}) boshqa guruhda ({conflict.group.name}) dars beradi.'
#                 })
#
#         return attrs
#
#
# # academics/serializers.py
#
# class CourseMinimalSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Course
#         fields = '__all__'
#
# class GroupListSerializer(serializers.ModelSerializer):
#     course = CourseMinimalSerializer(read_only=True)
#     room = RoomSerializer(read_only=True)
#     course_name = serializers.CharField(source='course.name', read_only=True)
#     room_name = serializers.CharField(source='room.name', read_only=True)
#     teacher_count = serializers.SerializerMethodField()
#     student_count = serializers.SerializerMethodField()
#     lesson_schedule = serializers.SerializerMethodField()
#
#     class Meta:
#         model = Group
#         fields = [
#             'id', 'name', 'course', 'course_name', 'room', 'room_name',
#             'start_date', 'end_date', 'status', 'lesson_schedule',
#             'teacher_count', 'student_count'
#         ]
#     def get_lesson_schedule(self, obj):
#         # LessonSchedule modelidan aynan shu guruhga tegishli kunlarni oladi
#         schedules = LessonSchedule.objects.filter(group=obj)
#         return [{
#             'day_type': s.day_type,
#             'start_time': s.start_time.strftime('%H:%M') if s.start_time else None,
#             'end_time': s.end_time.strftime('%H:%M') if s.end_time else None
#         } for s in schedules]
#
#     def get_teacher_count(self, obj):
#         return obj.group.count()
#
#     def get_student_count(self, obj):
#         return obj.Sgroup_group.filter(left_at__isnull=True).count()
#
#
#
#     def get_teachers(self, obj):
#             # Guruhga biriktirilgan o'qituvchilarni olamiz
#             teachers = GroupTeacher.objects.filter(group=obj).select_related('teacher__user')
#
#             res = []
#             for t in teachers:
#                 # t bu GroupTeacher obyekti
#                 # t.teacher bu Employee obyekti
#                 # t.teacher.user bu User obyekti (Ism-sharif aynan shu yerda)
#
#                 res.append({
#                     "id": t.teacher.id,
#                     # MANA BU JOYNI TO'G'IRLASH KERAK:
#                     "full_name": t.teacher.user.full_name if t.teacher.user.full_name else t.teacher.user.email,
#                     "start_date": t.start_date,
#                     "end_date": t.end_date,
#                     "is_active": t.end_date is None
#                 })
#             return res
#
#     def get_students_count(self, obj):
#         """Talabalar soni"""
#         return StudentGroup.objects.filter(
#             group=obj,
#             left_at__isnull=True
#         ).count()
#
#     def get_lesson_schedule(self, obj):
#         """Dars jadvali"""
#         schedules = LessonSchedule.objects.filter(group=obj)
#         return [{
#             'day_type': s.day_type,
#             'start_time': s.start_time.strftime('%H:%M'),
#             'end_time': s.end_time.strftime('%H:%M')
#         } for s in schedules]
#
#     def get_days_until_end(self, obj):
#         """Tugashigacha qolgan kunlar"""
#         if obj.end_date:
#             delta = obj.end_date - date.today()
#             return delta.days if delta.days > 0 else 0
#         return None
#
#     def get_progress_percentage(self, obj):
#         """O'tilgan muddat foizi"""
#         if obj.start_date and obj.end_date:
#             total_days = (obj.end_date - obj.start_date).days
#             passed_days = (date.today() - obj.start_date).days
#             if total_days > 0:
#                 return min(round((passed_days / total_days) * 100, 1), 100)
#         return 0
#
#     def get_status_color(self, obj):
#         """Status rangi (tugashiga qarab)"""
#         days_left = self.get_days_until_end(obj)
#         if days_left is None:
#             return 'gray'
#         elif days_left <= 7:
#             return 'red'  # Tugashi yaqin
#         elif days_left <= 30:
#             return 'yellow'  # Bir oydan kam
#         else:
#             return 'green'  # Yaxshi
#
#
#
# class GroupDetailSerializer(serializers.ModelSerializer):
#     """Guruh batafsil ma'lumot"""
#     course = CourseMinimalSerializer()
#     room = RoomSerializer()
#     teachers = serializers.SerializerMethodField()
#     students = serializers.SerializerMethodField()
#     lesson_schedule = serializers.SerializerMethodField()
#     statistics = serializers.SerializerMethodField()
#
#     class Meta:
#         model = Group
#         fields = '__all__'
#
#
#     def get_teachers(self, obj):
#         teachers = GroupTeacher.objects.filter(group=obj).select_related('teacher', 'teacher__user')
#
#         result = []
#         for t in teachers:
#             teacher = t.teacher
#             user = getattr(teacher, 'user', None)
#
#             full_name = ""
#             if user:
#                 full_name = f"{user.first_name} {user.last_name}".strip()
#                 if not full_name:
#                     full_name = user.email
#
#             result.append({
#                 'id': str(teacher.id) if teacher else None,
#                 'full_name': full_name,
#                 'start_date': t.start_date,
#                 'end_date': t.end_date,
#                 'is_active': t.end_date is None
#             })
#
#         return result
#
#     def get_students(self, obj):
#         students = StudentGroup.objects.filter(
#             group=obj,
#             left_at__isnull=True
#         ).select_related('student')
#         return [{
#             'id': str(s.student.id),
#             'full_name': s.student.full_name,
#             'phone': s.student.phone_number,
#             'joined_at': s.joined_at
#         } for s in students]
#
#     def get_lesson_schedule(self, obj):
#         schedules = LessonSchedule.objects.filter(group=obj)
#         return [{
#             'id': str(s.id),
#             'day_type': s.day_type,
#             'start_time': s.start_time.strftime('%H:%M'),
#             'end_time': s.end_time.strftime('%H:%M')
#         } for s in schedules]
#
#     def get_statistics(self, obj):
#         total_students = StudentGroup.objects.filter(group=obj).count()
#         active_students = StudentGroup.objects.filter(
#             group=obj, left_at__isnull=True
#         ).count()
#         left_students = total_students - active_students
#
#         return {
#             'total_students': total_students,
#             'active_students': active_students,
#             'left_students': left_students,
#             'days_until_end': (obj.end_date - date.today()).days if obj.end_date else None,
#             'total_duration_days': (obj.end_date - obj.start_date).days if obj.end_date else None
#         }
#
#
# class GroupCreateUpdateSerializer(serializers.ModelSerializer):
#     """Guruh yaratish va yangilash uchun serializer"""
#     teacher_ids = serializers.ListField(
#         child=serializers.CharField(),
#         write_only=True,
#         required=False,
#         help_text="O'qituvchilar ID ro'yxati"
#     )
#
#     class Meta:
#         model = Group
#         fields = '__all__'
#         read_only_fields = ['id']
#
#     def validate(self, attrs):
#         """Validatsiyalar"""
#         start_date = attrs.get('start_date')
#         end_date = attrs.get('end_date')
#         room = attrs.get('room')
#         course = attrs.get('course')
#
#         # Update uchun eski qiymatlarni olish
#         if self.instance:
#             start_date = start_date or self.instance.start_date
#             end_date = end_date or self.instance.end_date
#             room = room or self.instance.room
#             course = course or self.instance.course
#
#         # 1. Start date end date dan kichik bo'lishi kerak
#         if start_date and end_date:
#             if start_date >= end_date:
#                 raise serializers.ValidationError({
#                     'end_date': 'Tugash sanasi boshlanish sanasidan katta bo\'lishi kerak.'
#                 })
#
#         # 2. Bir vaqtning o'zida bir xonada faqat bitta guruh bo'lishi mumkin
#         if room and start_date and end_date and course and course.lesson:
#             overlapping = Group.objects.filter(
#                 room=room,
#                 course__lesson=course.lesson,
#                 status='active'
#             ).filter(
#                 Q(start_date__lte=end_date) &
#                 Q(end_date__gte=start_date)
#             )
#
#             # Update uchun o'zini exclude qilish
#             if self.instance:
#                 overlapping = overlapping.exclude(pk=self.instance.pk)
#
#             if overlapping.exists():
#                 conflict = overlapping.first()
#                 raise serializers.ValidationError({
#                     'room': f'Bu xonada ({room.name}) shu vaqtda ({course.lesson}) boshqa guruh ({conflict.name}) bor. Boshqa xona yoki vaqt tanlang.'
#                 })
#
#         # 3. Guruhga o'qituvchi biriktirilishi kerak (faqat create uchun)
#         if not self.instance:  # Yangi guruh yaratilayotgan bo'lsa
#             teacher_ids = self.initial_data.get('teacher_ids', [])
#             if not teacher_ids:
#                 raise serializers.ValidationError({
#                     'teacher_ids': 'Guruhga kamida bitta o\'qituvchi biriktirilishi kerak.'
#                 })
#
#         return attrs
#
#     @transaction.atomic
#     def create(self, validated_data):
#         """Guruh yaratish va o'qituvchilarni biriktirish"""
#         teacher_ids = validated_data.pop('teacher_ids', [])
#
#         # Guruhni yaratish
#         group = Group.objects.create(**validated_data)
#
#         # O'qituvchilarni biriktirish
#         if teacher_ids:
#             self._assign_teachers(group, teacher_ids, validated_data['start_date'], validated_data['end_date'])
#
#         return group
#
#     @transaction.atomic
#     def update(self, instance, validated_data):
#         teacher_ids = validated_data.pop('teacher_ids', None)
#
#         for attr, value in validated_data.items():
#             setattr(instance, attr, value)
#         instance.save()
#
#         # Faqat teacher_ids yuborilgandagina o'zgartiramiz
#         if teacher_ids is not None:
#             # related_name orqali o'chirish (agar related_name="group" bo'lsa)
#             # ehtiyot bo'ling: Related name odatda 'group_teachers' bo'lishi kerak
#             instance.group.all().delete()
#             self._assign_teachers(instance, teacher_ids, instance.start_date, instance.end_date)
#
#         return instance
#
#     def _assign_teachers(self, group, teacher_ids, start_date, end_date):
#             """O'qituvchilarni guruhga biriktirish (Xatolarsiz variant)"""
#             # teacher_ids UUID yoki ID ekanligini tekshiramiz
#             teachers = Employee.objects.filter(id__in=teacher_ids)
#
#             if len(teachers) != len(teacher_ids):
#                 raise serializers.ValidationError({
#                     'teacher_ids': 'Ba\'zi o\'qituvchilar topilmadi.'
#                 })
#
#             for teacher in teachers:
#                 # group.organization_id_id — Djangoda ForeignKey obyektini emas,
#                 # bazadagi asl ID qiymatni (UUID string) olish usuli.
#                 group_teacher_data = {
#                     'group': group.id,
#                     'teacher': teacher.id,
#                     'start_date': start_date,
#                     'end_date': end_date,
#                     # Agar maydon nomi 'organization' bo'lsa '_id' qo'shing,
#                     # agar allaqachon 'organization_id' bo'lsa, shunday qolsin.
#                     'organization_id': getattr(group, 'organization_id', group.organization_id),
#                     'branch_id': getattr(group, 'branch_id', group.branch_id)
#                 }
#
#                 # Validatsiyadan oldin ma'lumotlarni tekshirib olish uchun:
#                 group_teacher_serializer = GroupTeacherSerializer(data=group_teacher_data)
#
#                 try:
#                     group_teacher_serializer.is_valid(raise_exception=True)
#                     group_teacher_serializer.save()
#                 except serializers.ValidationError as e:
#                     # Ichki xatolikni aniq ko'rsatish
#                     raise serializers.ValidationError({
#                         'teacher_assignment_error': e.detail,
#                         'debug_info': group_teacher_data # Xato bo'lsa, nima yuborilganini ko'rish uchun
#                     })
#
#     def to_representation(self, instance):
#         """Response uchun detali serializer ishlatish"""
#         return GroupDetailSerializer(instance, context=self.context).data
#
#
#
#
#
# # ============ 1. GURUH TO'LIQ MA'LUMOTLARI ============
#
# class GroupFullInfoSerializer(serializers.ModelSerializer):
#     """Kurs nomi, O'qituvchi, Narx, Mashg'ulot sanalan, Xona va sig'imi"""
#     course_name = serializers.CharField(source='course.name', read_only=True)
#     monthly_price = serializers.DecimalField(source='course.monthly_price', max_digits=10, decimal_places=2,
#                                              read_only=True)
#     room_name = serializers.CharField(source='room.name', read_only=True)
#     room_capacity = serializers.IntegerField(source='room.capacity', read_only=True)
#     teachers = serializers.SerializerMethodField()
#     schedule = serializers.SerializerMethodField()
#     student_count = serializers.SerializerMethodField()
#
#     class Meta:
#         model = Group
#         fields = '__all__'
#
#     def get_teachers(self, obj):
#         teachers = obj.group.all()
#         return [{
#             'id': t.teacher.id,
#             'name': f"{t.teacher.first_name} {t.teacher.last_name}"
#         } for t in teachers]
#
#     def get_schedule(self, obj):
#         schedules = obj.lesson_group.all()
#         return [{
#             'day_type': s.day_type,
#             'start_time': str(s.start_time),
#             'end_time': str(s.end_time)
#         } for s in schedules]
#
#     def get_student_count(self, obj):
#         return obj.Sgroup_group.filter(left_at__gte=timezone.now().date()).count()
#
#
# # ============ 2. DAVOMAT ============
#
# class AttendanceSerializer(serializers.ModelSerializer):
#     student_name = serializers.CharField(source='student_group.student.full_name', read_only=True)
#
#     class Meta:
#         model = Attendence
#         fields = '__all__'
#         read_only_fields = ['marked_by']
#
#     def validate(self, attrs):
#         lesson_date = attrs.get('lesson_date')
#         today = timezone.now().date()
#
#         # 3 kun chegarasi
#         if not (today - timedelta(days=3) <= lesson_date <= today + timedelta(days=3)):
#             raise serializers.ValidationError({
#                 'lesson_date': 'Davomat faqat 3 kun oldin va keyin qo\'yilishi mumkin.'
#             })
#
#         return attrs
#
#
# # ============ 3. O'QUVCHILAR RO'YXATI ============
#
# class StudentListSerializer(serializers.ModelSerializer):
#     student_name = serializers.CharField(source='student.full_name', read_only=True)
#     student_phone = serializers.CharField(source='student.phone_number', read_only=True)
#     group_name = serializers.CharField(source='group.name', read_only=True)
#
#     class Meta:
#         model = StudentGroup
#         fields = '__all__'
#     balance = serializers.SerializerMethodField()
#     groups  = serializers.SerializerMethodField()
#     teachers = serializers.SerializerMethodField()
#     last_lesson_date = serializers.SerializerMethodField()
#     status  = serializers.SerializerMethodField()
#
#     class Meta:
#         model  = Student
#         fields = '__all__'
#
#     def get_balance(self, obj):
#         b = obj.student_balances.first()
#         return float(b.balance) if b else 0
#
#     def get_groups(self, obj):
#         sgs = obj.studentgroup_student.filter(
#             left_at__isnull=True
#         ).select_related('group__course')
#         return [
#             {
#                 'id': sg.group.id,
#                 'name': sg.group.name,
#                 'course': sg.group.course.name if sg.group.course else '',
#                 'start_time': str(sg.group.start_date),
#             }
#             for sg in sgs
#         ]
#
#     def get_teachers(self, obj):
#         group_ids = obj.studentgroup_student.filter(
#             left_at__isnull=True
#         ).values_list('group_id', flat=True)
#         tgs = GroupTeacher.objects.filter(
#             group_id__in=group_ids
#         ).select_related('teacher__user').distinct()
#         return [
#             {'id': t.teacher.id, 'full_name': t.teacher.user.full_name}
#             for t in tgs
#         ]
#
#     def get_last_lesson_date(self, obj):
#         sg = obj.studentgroup_student.filter(
#             left_at__isnull=True
#         ).order_by('-joined_at').first()
#         return str(sg.joined_at) if sg else None
#
#     def get_status(self, obj):
#         active_sg = obj.studentgroup_student.filter(left_at__isnull=True).first()
#         if not active_sg:
#             return {'code': 'inactive', 'label': 'Faol emas'}
#         freeze = obj.studentfreezes_student.filter(freeze_end_date__isnull=True).first()
#         if freeze:
#             return {'code': 'frozen', 'label': 'Muzlatilgan'}
#         return {'code': 'active', 'label': 'Faol'}
#
# # ============ 5. GURUHGA ODAM QO'SHISH =======
#
#
# class SMSSerializer(serializers.Serializer):
#     message = serializers.CharField(max_length=500)
#     send_to = serializers.ChoiceField(choices=['all', 'students', 'parents'])
#
#
# # ============ 6. CHEGIRMALAR ============
#
# class DiscountSerializer(serializers.ModelSerializer):
#     student_name = serializers.CharField(source='student.full_name', read_only=True)
#     course_name = serializers.CharField(source='course.name', read_only=True)
#
#     class Meta:
#         model = StudentPricing
#         fields = '__all__'
#         read_only_fields = ['created_by']
#
#
# # ============ 7. IMTIHONLAR ============
#
# class ExamSerializer(serializers.ModelSerializer):
#     group_name = serializers.CharField(source='group.name', read_only=True)
#
#     class Meta:
#         model = Exams
#         fields = '__all__'
#         read_only_fields = ['created_by']
#
#
#
#
#
# # ============ GURUHGA ODAM QO'SHISH - VALIDATSIYA BILAN ============
#
# class AddStudentSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = StudentGroup
#         fields = '__all__'
#
#     def validate(self, attrs):
#         """Validatsiyalar"""
#         student = attrs.get('student')
#         group = attrs.get('group')
#
#         # 1. Guruh active ekanligini tekshirish
#         if group and group.status != 'active':
#             raise serializers.ValidationError({
#                 'group': 'Faqat faol guruhlarga talaba qo\'shish mumkin.'
#             })
#
#         # 2. Talaba allaqachon guruhda emasligini tekshirish
#         if student and group:
#             existing = StudentGroup.objects.filter(
#                 student=student,
#                 group=group,
#                 left_at__gte=timezone.now().date()
#             )
#
#             if existing.exists():
#                 raise serializers.ValidationError({
#                     'student': 'Bu talaba allaqachon guruhda.'
#                 })
#
#         # 3. Xona sig'imi tekshiruvi
#         if group and group.room:
#             current_count = StudentGroup.objects.filter(
#                 group=group,
#                 left_at__gte=timezone.now().date()
#             ).count()
#
#             if current_count >= group.room.capacity:
#                 raise serializers.ValidationError({
#                     'group': f'Guruh to\'lgan! Xona sig\'imi: {group.room.capacity}, hozir: {current_count} ta talaba.'
#                 })
#
#         return attrs
#
#
# # ============ YANGI VAZIFA: O'QUVCHI QIDIRISH VA FAOLLASHTIRISH ============
#
#
#
#
# # 1. O'quvchini qidirish uchun serializer
# class StudentSearchSerializer(serializers.ModelSerializer):
#     """O'quvchini ismi yoki telefon raqami bo'yicha qidirish"""
#     balance = serializers.SerializerMethodField()
#     groups_count = serializers.SerializerMethodField()
#
#     class Meta:
#         model = Student
#         fields = '__all__'
#
#     def get_balance(self, obj):
#         """Talaba balansi"""
#         try:
#             student_balance = obj.Sbalances_student.first()
#             return float(student_balance.balance) if student_balance else 0.0
#         except:
#             return 0.0
#
#     def get_groups_count(self, obj):
#         """Nechta guruhda"""
#         return obj.Sgroup_student.filter(
#             left_at__gte=timezone.now().date()
#         ).count()
#
#
# # 2. Guruhga qo'shish uchun serializer (yangilangan versiya)
# class AddStudentToGroupSerializer(serializers.ModelSerializer):
#     """Guruhga talaba qo'shish"""
#
#     class Meta:
#         model = StudentGroup
#         fields = ['student', 'group', 'joined_at', 'left_at', 'end_date']
#
#     def validate(self, attrs):
#         """Validatsiyalar"""
#         student = attrs.get('student')
#         group = attrs.get('group')
#
#         # 1. Guruh active ekanligini tekshirish
#         if group and group.status != 'active':
#             raise serializers.ValidationError({
#                 'group': 'Faqat faol guruhlarga talaba qo\'shish mumkin.'
#             })
#
#         # 2. Talaba allaqachon guruhda emasligini tekshirish
#         if student and group:
#             existing = StudentGroup.objects.filter(
#                 student=student,
#                 group=group,
#                 left_at__gte=timezone.now().date()
#             )
#
#             if existing.exists():
#                 raise serializers.ValidationError({
#                     'student': 'Bu talaba allaqachon guruhda.'
#                 })
#
#         # 3. Xona sig'imi tekshiruvi
#         if group and group.room:
#             current_count = StudentGroup.objects.filter(
#                 group=group,
#                 left_at__gte=timezone.now().date()
#             ).count()
#
#             if current_count >= group.room.capacity:
#                 raise serializers.ValidationError({
#                     'group': f'Guruh to\'lgan! Xona sig\'imi: {group.room.capacity}, hozir: {current_count} ta talaba.'
#                 })
#
#         return attrs
#
#
# # 3. Talaba faollashtirish uchun serializer
# class ActivateStudentSerializer(serializers.Serializer):
#     """
#     Talabani faollashtirish (balansga pul kiritilganda)
#     Bu API StudentBalances ga pul qo'shadi va talabani faol qiladi
#     """
#     amount = serializers.DecimalField(
#         max_digits=12,
#         decimal_places=2,
#         min_value=0.01,
#         help_text="Qo'shiladigan pul miqdori"
#     )
#     payment_type = serializers.ChoiceField(
#         choices=[('cash', 'Naqd'), ('card', 'Karta'), ('transfer', 'O\'tkazma')],
#         help_text="To'lov turi"
#     )
#     comment = serializers.CharField(
#         max_length=500,
#         required=False,
#         allow_blank=True,
#         help_text="Izoh"
#     )
#
#     def validate_amount(self, value):
#         """Pul miqdori musbat bo'lishi kerak"""
#         if value <= 0:
#             raise serializers.ValidationError('Pul miqdori 0 dan katta bo\'lishi kerak.')
#         return value
#
#     def activate_student(self, student, validated_data, user):
#         """
#         Talabani faollashtirish:
#         1. StudentBalances ga pul qo'shish
#         2. StudentTransactions yaratish
#         """
#         from django.db import transaction
#         from .models import StudentTarnsactions
#
#         amount = validated_data['amount']
#         payment_type = validated_data['payment_type']
#         comment = validated_data.get('comment', 'Talaba faollashtirildi')
#
#         with transaction.atomic():
#             # 1. Balance yaratish yoki yangilash
#             student_balance, created = StudentBalances.objects.get_or_create(
#                 student=student,
#                 defaults={'balance': 0}
#             )
#
#             # Balansni yangilash
#             student_balance.balance += amount
#             student_balance.save()
#
#             # 2. Transaction yaratish
#             StudentTarnsactions.objects.create(
#                 student=student,
#                 transaction_type='payment',
#                 amount=amount,
#                 payment_type=payment_type,
#                 transaction_date=timezone.now(),
#                 accepted_by=user,
#                 comment=comment
#             )
#
#             return {
#                 'student_id': student.id,
#                 'student_name': student.full_name,
#                 'old_balance': float(student_balance.balance - amount),
#                 'added_amount': float(amount),
#                 'new_balance': float(student_balance.balance),
#                 'status': 'active',
#                 'message': 'Talaba muvaffaqiyatli faollashtirildi'
#             }
#
#
# # ============ ONLAYN DARSLAR SERIALIZERS ============
#
# from rest_framework import serializers
# from .models.lesson import OnlineLesson
#
#
# class OnlineLessonListSerializer(serializers.ModelSerializer):
#     """Ro'yxat uchun"""
#     group_name = serializers.CharField(source='group.name', read_only=True)
#     created_by_name = serializers.SerializerMethodField()
#
#     class Meta:
#         model = OnlineLesson
#         fields = '__all__'
#
#     def get_created_by_name(self, obj):
#         if obj.created_by:
#             return f"{obj.created_by.first_name} {obj.created_by.last_name}"
#         return None
#
#
# class OnlineLessonDetailSerializer(serializers.ModelSerializer):
#     """Detallar uchun"""
#     group_name = serializers.CharField(source='group.name', read_only=True)
#     created_by_name = serializers.SerializerMethodField()
#     file_url = serializers.SerializerMethodField()
#
#     class Meta:
#         model = OnlineLesson
#         fields = '__all__'
#
#     def get_created_by_name(self, obj):
#         if obj.created_by:
#             return f"{obj.created_by.first_name} {obj.created_by.last_name}"
#         return None
#
#     def get_file_url(self, obj):
#         if obj.file:
#             request = self.context.get('request')
#             if request:
#                 return request.build_absolute_uri(obj.file.url)
#             return obj.file.url
#         return None
#
#
# class OnlineLessonCreateUpdateSerializer(serializers.ModelSerializer):
#     """Yaratish/Yangilash"""
#
#     class Meta:
#         model = OnlineLesson
#         fields = '__all__'
#         read_only_fields = ['id']
#
#     def validate(self, attrs):
#         """Validatsiyalar"""
#         content_type = attrs.get('content_type')
#
#         if content_type == 'video':
#             if not attrs.get('video_url') and not attrs.get('file'):
#                 raise serializers.ValidationError({
#                     'video_url': 'Video uchun video_url yoki file majburiy.'
#                 })
#
#         elif content_type == 'document' or content_type == 'image':
#             if not attrs.get('file'):
#                 raise serializers.ValidationError({
#                     'file': f'{content_type} uchun file majburiy.'
#                 })
#
#         elif content_type == 'link':
#             if not attrs.get('external_link'):
#                 raise serializers.ValidationError({
#                     'external_link': 'Havola uchun external_link majburiy.'
#                 })
#
#         elif content_type == 'text':
#             if not attrs.get('text_content'):
#                 raise serializers.ValidationError({
#                     'text_content': 'Matn uchun text_content majburiy.'
#                 })
#
#         return attrs
#
#     def to_representation(self, instance):
#         return OnlineLessonDetailSerializer(instance, context=self.context).data
#
#
# # ============ STUDENT DISCOUNT SERIALIZERS ============
#
#
#
#
# class StudentDiscountSerializer(serializers.ModelSerializer):
#     """O'quvchi chegirmasi serializer"""
#
#     student_name = serializers.CharField(source='student.full_name', read_only=True)
#     course_name = serializers.CharField(source='course.name', read_only=True)
#     original_price = serializers.DecimalField(source='course.monthly_price', max_digits=10, decimal_places=2,
#                                               read_only=True)
#     discount_amount = serializers.SerializerMethodField()
#     discount_percentage = serializers.SerializerMethodField()
#     created_by_name = serializers.SerializerMethodField()
#     is_active = serializers.SerializerMethodField()
#
#     class Meta:
#         model = StudentPricing
#         fields = '__all__'
#         read_only_fields = ['id', 'created_by', 'created_at']
#
#     def get_discount_amount(self, obj):
#         """Chegirma miqdori"""
#         if obj.course:
#             return float(obj.course.monthly_price - obj.price_override)
#         return 0
#
#     def get_discount_percentage(self, obj):
#         """Chegirma foizi"""
#         if obj.course and obj.course.monthly_price > 0:
#             discount = ((obj.course.monthly_price - obj.price_override) / obj.course.monthly_price) * 100
#             return round(float(discount), 2)
#         return 0
#
#     def get_created_by_name(self, obj):
#         if obj.created_by:
#             return f"{obj.created_by.first_name} {obj.created_by.last_name}"
#         return None
#
#     def get_is_active(self, obj):
#         """Chegirma hozir aktivmi?"""
#         today = timezone.now().date()
#         return obj.start_date <= today <= obj.end_date
#
#     def validate(self, attrs):
#         """Validatsiyalar"""
#         student = attrs.get('student') or (self.instance.student if self.instance else None)
#         course = attrs.get('course') or (self.instance.course if self.instance else None)
#         start_date = attrs.get('start_date') or (self.instance.start_date if self.instance else None)
#         end_date = attrs.get('end_date') or (self.instance.end_date if self.instance else None)
#         price_override = attrs.get('price_override')
#
#         # 1. Start date < end date
#         if start_date and end_date and start_date >= end_date:
#             raise serializers.ValidationError({
#                 'end_date': 'Tugash sanasi boshlanish sanasidan katta bo\'lishi kerak.'
#             })
#
#         # 2. Narx musbat
#         if price_override is not None and price_override < 0:
#             raise serializers.ValidationError({
#                 'price_override': 'Narx 0 dan katta bo\'lishi kerak.'
#             })
#
#         # 3. Narx asl narxdan kichik bo'lishi kerak
#         if price_override and course and price_override > course.monthly_price:
#             raise serializers.ValidationError({
#                 'price_override': f'Chegirma narxi asl narxdan ({course.monthly_price}) katta bo\'lishi mumkin emas.'
#             })
#
#         # 4. Bir o'quvchi uchun bir kurs bo'yicha faqat bitta chegirma
#         if student and course:
#             existing = StudentPricing.objects.filter(
#                 student=student,
#                 course=course
#             ).filter(
#                 Q(start_date__lte=end_date) & Q(end_date__gte=start_date)
#             )
#
#             if self.instance:
#                 existing = existing.exclude(pk=self.instance.pk)
#
#             if existing.exists():
#                 raise serializers.ValidationError({
#                     'student': 'Bu o\'quvchi uchun bu vaqt oralig\'ida allaqachon chegirma mavjud.'
#                 })
#
#         return attrs
#
#
# class CreateStudentDiscountSerializer(serializers.Serializer):
#     """Guruh uchun o'quvchiga chegirma qo'shish"""
#
#     price_override = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0)
#     reason = serializers.CharField(max_length=500)
#     start_date = serializers.DateField()
#     end_date = serializers.DateField()
#
#     def validate(self, attrs):
#         """Validatsiyalar"""
#         start_date = attrs.get('start_date')
#         end_date = attrs.get('end_date')
#
#         if start_date >= end_date:
#             raise serializers.ValidationError({
#                 'end_date': 'Tugash sanasi boshlanish sanasidan katta bo\'lishi kerak.'
#             })
#
#         return attrs
#
#     def create_discount(self, student, group, validated_data, user):
#         """Chegirma yaratish"""
#
#         # Guruhning kursi
#         course = group.course
#
#         # Narx tekshiruvi
#         price_override = validated_data['price_override']
#         if price_override > course.monthly_price:
#             raise serializers.ValidationError({
#                 'price_override': f'Chegirma narxi asl narxdan ({course.monthly_price}) katta bo\'lishi mumkin emas.'
#             })
#
#         # Mavjud chegirma bormi?
#         start_date = validated_data['start_date']
#         end_date = validated_data['end_date']
#
#         existing = StudentPricing.objects.filter(
#             student=student,
#             course=course
#         ).filter(
#             Q(start_date__lte=end_date) & Q(end_date__gte=start_date)
#         )
#
#         if existing.exists():
#             raise serializers.ValidationError({
#                 'error': 'Bu o\'quvchi uchun bu vaqt oralig\'ida allaqachon chegirma mavjud.'
#             })
#
#         # Chegirma yaratish
#         discount = StudentPricing.objects.create(
#             student=student,
#             course=course,
#             price_override=price_override,
#             reason=validated_data['reason'],
#             start_date=start_date,
#             end_date=end_date,
#             created_by=user
#         )
#
#         return discount
#
#
# # ============ DARS SANASI BOSHQARUVI SERIALIZERS ============
#
#
#
#
# class LessonScheduleListSerializer(serializers.ModelSerializer):
#     group_name = serializers.CharField(source='group.name', read_only=True)
#
#     # MANA SHU QATOR ISMNI OLIB KELADI:
#     teacher_name = serializers.SerializerMethodField()
#
#     day_type_display = serializers.CharField(source='get_day_type_display', read_only=True)
#     duration = serializers.SerializerMethodField()
#
#     class Meta:
#         model = LessonSchedule
#         fields = [
#             'id', 'group', 'group_name', 'teacher', 'teacher_name', # 'teacher' bu ID, 'teacher_name' bu ISMI
#             'day_type', 'day_type_display', 'start_time', 'end_time',
#             'duration', 'created_at'
#         ]
#
#     def get_teacher_name(self, obj):
#         # Mantiq: LessonSchedule -> Employee -> User -> First/Last Name
#         if obj.teacher and obj.teacher.user:
#             user = obj.teacher.user
#             full_name = f"{user.first_name} {user.last_name}".strip()
#             return full_name if full_name else user.username
#         return "Biriktirilmagan"
#
#     def get_duration(self, obj):
#         from datetime import datetime
#         start = datetime.combine(datetime.today(), obj.start_time)
#         end = datetime.combine(datetime.today(), obj.end_time)
#         return (end - start).seconds // 60
#
# class LessonScheduleDetailSerializer(serializers.ModelSerializer):
#     """Dars detallari"""
#
#     group_info = serializers.SerializerMethodField()
#     duration_minutes = serializers.SerializerMethodField()
#
#     class Meta:
#         model = LessonSchedule
#         fields = '__all__'
#
#     def get_group_info(self, obj):
#         return {
#             'id': obj.group.id,
#             'name': obj.group.name,
#             'status': obj.group.status,
#             'start_date': obj.group.start_date,
#             'end_date': obj.group.end_date
#         }
#
#     def get_duration_minutes(self, obj):
#         from datetime import datetime
#
#         start = datetime.combine(datetime.today(), obj.start_time)
#         end = datetime.combine(datetime.today(), obj.end_time)
#
#         return (end - start).seconds // 60
#
#
# class MoveLessonDateSerializer(serializers.Serializer):
#     """Dars sanasini ko'chirish"""
#
#     new_start_time = serializers.TimeField()
#     new_end_time = serializers.TimeField()
#     new_day_type = serializers.ChoiceField(
#         choices=LessonSchedule.DAY_TYPE,
#         required=False
#     )
#
#     def validate(self, attrs):
#         """Validatsiyalar"""
#         new_start_time = attrs.get('new_start_time')
#         new_end_time = attrs.get('new_end_time')
#
#         # Start < End
#         if new_start_time >= new_end_time:
#             raise serializers.ValidationError({
#                 'new_end_time': 'Tugash vaqti boshlanish vaqtidan katta bo\'lishi kerak.'
#             })
#
#         return attrs
#
#     def move_lesson(self, lesson, validated_data):
#         """Darsni ko'chirish"""
#
#         new_start_time = validated_data['new_start_time']
#         new_end_time = validated_data['new_end_time']
#         new_day_type = validated_data.get('new_day_type', lesson.day_type)
#
#         # To'qnashuv tekshiruvi
#         conflicts = LessonSchedule.objects.filter(
#             group__room=lesson.group.room,
#             day_type=new_day_type
#         ).filter(
#             Q(start_time__lt=new_end_time) & Q(end_time__gt=new_start_time)
#         ).exclude(pk=lesson.pk)
#
#         if conflicts.exists():
#             conflict = conflicts.first()
#             raise serializers.ValidationError({
#                 'error': f'Bu vaqtda xonada boshqa dars bor: {conflict.group.name} ({conflict.start_time}-{conflict.end_time})'
#             })
#
#         # O'qituvchi to'qnashuvi
#         from .models import GroupTeacher
#
#         teachers = GroupTeacher.objects.filter(group=lesson.group)
#
#         for gt in teachers:
#             teacher_conflicts = LessonSchedule.objects.filter(
#                 group__group__teacher=gt.teacher,
#                 day_type=new_day_type
#             ).filter(
#                 Q(start_time__lt=new_end_time) & Q(end_time__gt=new_start_time)
#             ).exclude(pk=lesson.pk)
#
#             if teacher_conflicts.exists():
#                 conflict = teacher_conflicts.first()
#                 raise serializers.ValidationError({
#                     'error': f'O\'qituvchi bu vaqtda boshqa guruhda dars beradi: {conflict.group.name}'
#                 })
#
#         # Sanani ko'chirish
#         lesson.start_time = new_start_time
#         lesson.end_time = new_end_time
#         lesson.day_type = new_day_type
#         lesson.save()
#
#         return lesson
#
#
# # ==================== SERIALIZERS ====================
#
# class LeaveReportFilterSerializer(serializers.Serializer):
#     """Filtrlash uchun"""
#     leave_date_start = serializers.DateField(required=False, help_text="Tark etish sanasi (dan)")
#     leave_date_end = serializers.DateField(required=False, help_text="Tark etish sanasi (gacha)")
#     search = serializers.CharField(required=False, help_text="Ism yoki telefon")
#     course_id = serializers.IntegerField(required=False, help_text="Kurs ID")
#     group_id = serializers.IntegerField(required=False, help_text="Guruh ID")
#     teacher_id = serializers.IntegerField(required=False, help_text="O'qituvchi ID")
#     archived_by_id = serializers.IntegerField(required=False, help_text="Arxivlagan xodim ID")
#     leave_reason_id = serializers.IntegerField(required=False, help_text="Sabab ID")
#
#
# class StudentLeaveReportSerializer(serializers.Serializer):
#     """Tark etgan talaba ma'lumotlari"""
#
#     student_id = serializers.IntegerField()
#     full_name = serializers.CharField()
#     phone_number = serializers.CharField()
#     course_name = serializers.CharField()
#     group_name = serializers.CharField()
#     teacher_name = serializers.CharField()
#     status = serializers.CharField()
#     archived_by = serializers.CharField()
#     leave_date = serializers.DateTimeField()
#     leave_reason = serializers.CharField()
#     comment = serializers.CharField()
#
#
#
#
#
# # ==================== SERIALIZERS ====================
#
# class CancelLessonSerializer(serializers.Serializer):
#     """Darsni bekor qilish"""
#
#     lesson_date = serializers.DateField(help_text="Dars sanasi")
#     cancellation_reason = serializers.CharField(
#         max_length=500,
#         required=False,
#         allow_blank=True,
#         help_text="Sabab"
#     )
#     recalculate_balance = serializers.BooleanField(
#         default=False,
#         help_text="Balansni qayta hisoblash"
#     )
#
#     def validate_lesson_date(self, value):
#         """O'tgan kunni bekor qilib bo'lmaydi"""
#         if value < date.today():
#             raise serializers.ValidationError(
#                 "O'tgan kunlarni bekor qilib bo'lmaydi."
#             )
#         return value
#
#     def validate(self, attrs):
#         """Dublikat tekshiruvi"""
#         # Bu dars allaqachon bekor qilinganmi?
#         lesson_schedule_id = self.context.get('lesson_schedule_id')
#         lesson_date = attrs.get('lesson_date')
#
#         entity_id = f"{lesson_schedule_id}_{lesson_date}"
#
#         existing = AuditLog.objects.filter(
#             entity_type='cancelled_lesson',
#             entity_id=entity_id,
#             action='cancelled'
#         ).exclude(
#             new_data__has_key='restored_at'  # Tiklanmagan
#         ).exists()
#
#         if existing:
#             raise serializers.ValidationError(
#                 "Bu dars allaqachon bekor qilingan."
#             )
#
#         return attrs
#
#     def cancel_lesson(self, group, lesson_schedule, validated_data, user):
#         """Darsni bekor qilish"""
#
#         lesson_date = validated_data['lesson_date']
#         recalculate = validated_data.get('recalculate_balance', False)
#         reason = validated_data.get('cancellation_reason', '')
#
#         with transaction.atomic():
#
#             # Dars ma'lumotlari
#             old_data = {
#                 'lesson_schedule_id': lesson_schedule.id,
#                 'group_id': group.id,
#                 'group_name': group.name,
#                 'lesson_date': str(lesson_date),
#                 'day_type': lesson_schedule.day_type,
#                 'start_time': str(lesson_schedule.start_time),
#                 'end_time': str(lesson_schedule.end_time),
#             }
#
#             total_refunded = 0
#             refund_per_student = 0
#             students_count = 0
#
#             # Balans qayta hisoblash
#             if recalculate:
#                 monthly_price = group.course.monthly_price
#                 lessons_per_month = group.course.lesson_month
#
#                 refund_per_student = monthly_price / lessons_per_month if lessons_per_month > 0 else 0
#
#                 # Faol talabalar
#                 active_students = StudentGroup.objects.filter(
#                     group=group,
#                     left_at__gte=timezone.now().date()
#                 )
#
#                 students_count = active_students.count()
#
#                 for student_group in active_students:
#                     student = student_group.student
#
#                     # Balance
#                     student_balance, created = StudentBalances.objects.get_or_create(
#                         student=student,
#                         defaults={'balance': 0}
#                     )
#
#                     # Pul qaytarish
#                     student_balance.balance += refund_per_student
#                     student_balance.save()
#
#                     # Transaction
#                     StudentTarnsactions.objects.create(
#                         student=student,
#                         group=group,
#                         transaction_type='refund',
#                         amount=refund_per_student,
#                         payment_type='correction',
#                         transaction_date=timezone.now(),
#                         accepted_by=user,
#                         comment=f"Dars bekor qilindi: {lesson_date} - {reason}"
#                     )
#
#                     total_refunded += refund_per_student
#
#             # AuditLog ga saqlash
#             entity_id = f"{lesson_schedule.id}_{lesson_date}"
#
#             new_data = {
#                 'cancelled': True,
#                 'cancelled_at': str(timezone.now()),
#                 'cancelled_by_id': user.id,
#                 'cancelled_by_name': f"{user.first_name} {user.last_name}",
#                 'reason': reason,
#                 'recalculated_balance': recalculate,
#                 'refund_per_student': float(refund_per_student),
#                 'total_refunded': float(total_refunded),
#                 'students_count': students_count
#             }
#
#             audit = AuditLog.objects.create(
#                 entity_type='cancelled_lesson',
#                 entity_id=entity_id,
#                 action='cancelled',
#                 old_data=old_data,
#                 new_data=new_data,
#                 performed_by=user,
#                 performed_by_role='admin'
#             )
#
#             return audit
#
#
# class RestoreLessonSerializer(serializers.Serializer):
#     """Darsni qayta tiklash"""
#
#     restore_note = serializers.CharField(
#         max_length=500,
#         required=False,
#         allow_blank=True,
#         help_text="Izoh"
#     )
#
#     def restore_lesson(self, cancelled_audit, user):
#         """Qayta tiklash - balans avtomatik qaytarilmaydi!"""
#
#         with transaction.atomic():
#             # Cancelled_audit ni yangilash
#             if 'restored_at' in cancelled_audit.new_data:
#                 raise serializers.ValidationError(
#                     "Bu dars allaqachon tiklangan."
#                 )
#
#             # new_data ga restored ma'lumotini qo'shish
#             cancelled_audit.new_data['restored_at'] = str(timezone.now())
#             cancelled_audit.new_data['restored_by_id'] = user.id
#             cancelled_audit.new_data['restored_by_name'] = f"{user.first_name} {user.last_name}"
#             cancelled_audit.new_data['restore_note'] = self.validated_data.get('restore_note', '')
#             cancelled_audit.save()
#
#             return cancelled_audit
#
#
# # chegirma berish
#
#
# # ==================== SERIALIZERS ====================
#
# class DiscountPriceSerializer(serializers.Serializer):
#     """Chegirmali narx"""
#
#     price_override = serializers.DecimalField(
#         max_digits=10,
#         decimal_places=2,
#         min_value=0,
#         help_text="Yangi narx (chegirmali)"
#     )
#     reason = serializers.CharField(
#         max_length=500,
#         required=False,
#         allow_blank=True,
#         help_text="Sabab (tavsiya etiladi)"
#     )
#     start_date = serializers.DateField(
#         help_text="Qaysi sanadan boshlab"
#     )
#     end_date = serializers.DateField(
#         help_text="Qaysi sanagacha"
#     )
#
#     def validate(self, attrs):
#         """Validatsiyalar"""
#         start_date = attrs.get('start_date')
#         end_date = attrs.get('end_date')
#
#         # 1. Start < End
#         if start_date >= end_date:
#             raise serializers.ValidationError({
#                 'end_date': 'Tugash sanasi boshlanish sanasidan katta bo\'lishi kerak.'
#             })
#
#         return attrs
#
#
# class StudentDiscountSerializer(serializers.ModelSerializer):
#     """Talaba chegirmasi (ko'rish uchun)"""
#
#     student_name = serializers.CharField(source='student.full_name', read_only=True)
#     course_name = serializers.CharField(source='course.name', read_only=True)
#     original_price = serializers.DecimalField(
#         source='course.monthly_price',
#         max_digits=10,
#         decimal_places=2,
#         read_only=True
#     )
#     discount_amount = serializers.SerializerMethodField()
#     is_active = serializers.SerializerMethodField()
#     created_by_name = serializers.SerializerMethodField()
#
#     class Meta:
#         model = StudentPricing
#         fields = '__all__'
#
#     def get_discount_amount(self, obj):
#         """Chegirma miqdori"""
#         if obj.course:
#             return float(obj.course.monthly_price - obj.price_override)
#         return 0
#
#     def get_is_active(self, obj):
#         """Hozir faolmi?"""
#         today = timezone.now().date()
#         return obj.start_date <= today <= obj.end_date
#
#     def get_created_by_name(self, obj):
#         if obj.created_by:
#             return f"{obj.created_by.first_name} {obj.created_by.last_name}"
#         return None
#
#
# # ==================== HELPER FUNCTIONS ====================
#
# def calculate_refund(student, old_price, new_price):
#     """
#     Farqni hisoblash va qaytarish
#
#     Args:
#         student: Student object
#         old_price: Eski narx (asl)
#         new_price: Yangi narx (chegirmali)
#
#     Returns:
#         refund_amount: Qaytariladigan summa
#     """
#
#     # Agar yangi narx kichik bo'lsa - pul qaytarish kerak
#     if new_price < old_price:
#         refund = old_price - new_price
#
#         # Balansga qo'shish
#         balance, created = StudentBalances.objects.get_or_create(
#             student=student,
#             defaults={'balance': 0}
#         )
#
#         balance.balance += refund
#         balance.save()
#
#         return refund
#
#     return 0
#
#
# from rest_framework import serializers
# from .models import Group, GroupTeacher, StudentGroup
# from .models import Student, StudentGroupLeaves, StudentFreezes
# from accounts.models import Employee
#
#
# class EmployeeMinimalSerializer(serializers.ModelSerializer):
#     """Xodim minimal ma'lumotlari"""
#
#     class Meta:
#         model = Employee
#         fields = '__all__'
#
#
# class StudentMinimalSerializer(serializers.ModelSerializer):
#     """Talaba minimal ma'lumotlari"""
#
#     class Meta:
#         model = Student
#         fields = '__all__'
#
#
# class GroupHistorySerializer(serializers.Serializer):
#     """Guruh tarixi uchun umumiy serializer"""
#     action_type = serializers.CharField()
#     action_date = serializers.DateTimeField()
#     performed_by = EmployeeMinimalSerializer()
#     details = serializers.DictField()
#
#
# class GroupTeacherHistorySerializer(serializers.ModelSerializer):
#     """O'qituvchi tayinlash/almashtirish tarixi"""
#     teacher = EmployeeMinimalSerializer()
#     action_type = serializers.SerializerMethodField()
#
#     class Meta:
#         model = GroupTeacher
#         fields = '__all__'
#
#     def get_action_type(self, obj):
#         return "O'qituvchi tayinlandi"
#
#
# class StudentGroupHistorySerializer(serializers.ModelSerializer):
#     """Talaba guruhga qo'shilish tarixi"""
#     student = StudentMinimalSerializer()
#     action_type = serializers.SerializerMethodField()
#
#     class Meta:
#         model = StudentGroup
#         fields = '__all__'
#
#     def get_action_type(self, obj):
#         if obj.left_at:
#             return "Talaba guruhdan chiqdi"
#         return "Talaba guruhga qo'shildi"
#
#
# class StudentLeaveHistorySerializer(serializers.ModelSerializer):
#     """Talaba ketish tarixi"""
#     student = StudentMinimalSerializer()
#     leave_reason = serializers.StringRelatedField()
#     created_by = EmployeeMinimalSerializer()
#
#     class Meta:
#         model = StudentGroupLeaves
#         fields = '__all__'
#
#
# class StudentFreezeHistorySerializer(serializers.ModelSerializer):
#     """Talaba muzlatish tarixi"""
#     student = StudentMinimalSerializer()
#     created_by = EmployeeMinimalSerializer()
#
#     class Meta:
#         model = StudentFreezes
#         fields = '__all__'
#
#
#
#
#
# class GroupDetailedHistorySerializer(serializers.Serializer):
#     """Guruh to'liq tarixi - barcha harakatlar birlashtirilgan"""
#     teachers = GroupTeacherHistorySerializer(many=True)
#     students_joined = StudentGroupHistorySerializer(many=True)
#     students_left = StudentLeaveHistorySerializer(many=True)
#     freezes = StudentFreezeHistorySerializer(many=True)
#     audit_logs = AuditLogSerializer(many=True)
#     timeline = serializers.ListField()  # Chronological timeline
#
#
# from rest_framework import serializers
# from .models import (
#     Student, StudentGroup, StudentFreezes,
#     StudentGroupLeaves, StudentBalances, StudentTarnsactions
# )
# from .models import Group
# from accounts.models import Employee
# from decimal import Decimal
#
#
# class StudentTransferSerializer(serializers.Serializer):
#     """Talabani boshqa guruhga o'tkazish"""
#     student_id = serializers.UUIDField()
#     from_group_id = serializers.UUIDField()
#     to_group_id = serializers.UUIDField()
#     transfer_date = serializers.DateField(default=timezone.now().date)
#     recalc_balance = serializers.BooleanField(default=True)
#     reason = serializers.CharField(required=False, allow_blank=True)
#
#     def validate(self, data):
#         # Student mavjudligini tekshirish
#         try:
#             student = Student.objects.get(id=data['student_id'])
#         except Student.DoesNotExist:
#             raise serializers.ValidationError("Talaba topilmadi")
#
#         # From group tekshirish
#         try:
#             from_group = Group.objects.get(id=data['from_group_id'])
#         except Group.DoesNotExist:
#             raise serializers.ValidationError("Asl guruh topilmadi")
#
#         # To group tekshirish
#         try:
#             to_group = Group.objects.get(id=data['to_group_id'])
#         except Group.DoesNotExist:
#             raise serializers.ValidationError("Yangi guruh topilmadi")
#
#         # Talaba asl guruhda borligini tekshirish
#         if not StudentGroup.objects.filter(
#                 student=student,
#                 group=from_group,
#                 left_at__isnull=True
#         ).exists():
#             raise serializers.ValidationError("Talaba bu guruhda emas")
#
#         # Talaba yangi guruhda allaqachon borligini tekshirish
#         if StudentGroup.objects.filter(
#                 student=student,
#                 group=to_group,
#                 left_at__isnull=True
#         ).exists():
#             raise serializers.ValidationError("Talaba yangi guruhda allaqachon mavjud")
#
#         data['student'] = student
#         data['from_group'] = from_group
#         data['to_group'] = to_group
#
#         return data
#
#
# class StudentFreezeSerializer(serializers.ModelSerializer):
#     """Talabani muzlatish"""
#     student_id = serializers.UUIDField(write_only=True)
#     group_id = serializers.UUIDField(write_only=True)
#
#     class Meta:
#         model = StudentFreezes
#         fields = '__all__'
#         read_only_fields = ['id', 'created_at']
#
#     def validate(self, data):
#         # Sanalarni tekshirish
#         if data['freeze_end_date'] <= data['freeze_start_date']:
#             raise serializers.ValidationError(
#                 "Tugash sanasi boshlanish sanasidan katta bo'lishi kerak"
#             )
#
#         # Student mavjudligini tekshirish
#         try:
#             student = Student.objects.get(id=data['student_id'])
#             data['student'] = student
#         except Student.DoesNotExist:
#             raise serializers.ValidationError("Talaba topilmadi")
#
#         # Group mavjudligini tekshirish
#         try:
#             group = Group.objects.get(id=data['group_id'])
#             data['group'] = group
#         except Group.DoesNotExist:
#             raise serializers.ValidationError("Guruh topilmadi")
#
#         # Allaqachon muzlatilganligini tekshirish
#         overlapping = StudentFreezes.objects.filter(
#             student=student,
#             group=group,
#             freeze_start_date__lte=data['freeze_end_date'],
#             freeze_end_date__gte=data['freeze_start_date']
#         )
#
#         if overlapping.exists():
#             raise serializers.ValidationError(
#                 "Talaba bu muddat uchun allaqachon muzlatilgan"
#             )
#
#         return data
#
#     def create(self, validated_data):
#         # student_id va group_id ni o'chirish
#         student = validated_data.pop('student')
#         group = validated_data.pop('group')
#         validated_data.pop('student_id')
#         validated_data.pop('group_id')
#
#         # Created_by qo'shish
#         validated_data['student'] = student
#         validated_data['group'] = group
#         validated_data['created_by'] = self.context['request'].user
#
#         return super().create(validated_data)
#
#
# class StudentLeaveSerializer(serializers.Serializer):
#     """Talabani guruhdan chiqarish"""
#     student_id = serializers.UUIDField()
#     group_id = serializers.UUIDField()
#     leave_reason_id = serializers.UUIDField(required=False, allow_null=True)
#     leave_date = serializers.DateTimeField(default=timezone.now)
#     comment = serializers.CharField(required=False, allow_blank=True)
#     recalc_balance = serializers.BooleanField(default=True)
#     refound_amount = serializers.DecimalField(
#         max_digits=12, decimal_places=2, default=Decimal('0.00')
#     )
#
#     def validate(self, data):
#         # Student tekshirish
#         try:
#             student = Student.objects.get(id=data['student_id'])
#             data['student'] = student
#         except Student.DoesNotExist:
#             raise serializers.ValidationError("Talaba topilmadi")
#
#         # Group tekshirish
#         try:
#             group = Group.objects.get(id=data['group_id'])
#             data['group'] = group
#         except Group.DoesNotExist:
#             raise serializers.ValidationError("Guruh topilmadi")
#
#         # StudentGroup tekshirish
#         try:
#             student_group = StudentGroup.objects.get(
#                 student=student,
#                 group=group,
#                 left_at__isnull=True
#             )
#             data['student_group'] = student_group
#         except StudentGroup.DoesNotExist:
#             raise serializers.ValidationError("Talaba bu guruhda emas")
#
#         return data
#
#
# class BalanceRecalculationSerializer(serializers.Serializer):
#     """Balansni qayta hisoblash"""
#     student_id = serializers.UUIDField()
#     group_id = serializers.UUIDField(required=False, allow_null=True)
#     recalc_type = serializers.ChoiceField(
#         choices=['freeze', 'leave', 'transfer'],
#         required=True
#     )
#     freeze_days = serializers.IntegerField(required=False, default=0)
#
#     def validate(self, data):
#         try:
#             student = Student.objects.get(id=data['student_id'])
#             data['student'] = student
#         except Student.DoesNotExist:
#             raise serializers.ValidationError("Talaba topilmadi")
#
#         return data
#
#
#
#
#
# class GroupMinimalSerializer(serializers.ModelSerializer):
#     """Minimal group info"""
#
#     class Meta:
#         model = Group
#         fields = '__all__'
#
#
#
#
# class StudentGroupDetailSerializer(serializers.ModelSerializer):
#     """StudentGroup batafsil ma'lumot (GET uchun)"""
#     # Guruh ma'lumotlari
#     group_name = serializers.CharField(source='group.name', read_only=True)
#     course_name = serializers.CharField(source='group.course.name', read_only=True)
#     course_price = serializers.DecimalField(
#         source='group.course.monthly_price',
#         max_digits=12, decimal_places=2, read_only=True
#     )
#     group_status = serializers.CharField(source='group.status', read_only=True)
#     teacher = serializers.SerializerMethodField()
#     schedule = serializers.SerializerMethodField()
#
#     class Meta:
#         model = StudentGroup
#         fields = [
#             'id', 'student', 'group', 'group_name', 'course_name',
#             'course_price', 'group_status', 'teacher', 'schedule',
#             'joined_at', 'left_at', 'end_date'
#         ]
#
#     def get_teacher(self, obj):
#         tg = GroupTeacher.objects.filter(
#             group=obj.group
#         ).select_related('teacher__user').first()
#         if tg:
#             return {'id': tg.teacher.id, 'full_name': tg.teacher.user.full_name}
#         return None
#
#     def get_schedule(self, obj):
#         # lesson_group - bu Group modelidagi related_name deb hisoblaymiz
#         return [
#             {
#                 'day_type': s.day_type,
#                 'start_time': str(s.start_time),
#                 'end_time': str(s.end_time),
#             }
#             for s in obj.group.lesson_group.all()
#         ]
#
# class StudentGroupCreateUpdateSerializer(serializers.ModelSerializer):
#     """Yaratish va yangilash uchun (POST, PUT, PATCH)"""
#     class Meta:
#         model = StudentGroup
#         # Faqat foydalanuvchi yuborishi kerak bo'lgan maydonlar
#         fields = ['student', 'group', 'joined_at', 'left_at', 'end_date']
#
#     def validate(self, attrs):
#         # Validatsiya: qo'shilgan sana tugash sanasidan katta bo'lmasligi kerak
#         if attrs.get('joined_at') and attrs.get('end_date'):
#             if attrs['joined_at'] > attrs['end_date']:
#                 raise serializers.ValidationError("Qo'shilgan sana tugash sanasidan keyin bo'la olmaydi.")
#         return attrs
#
#     def create(self, validated_data):
#         group = validated_data.get('group')
#
#         # 1. Avval obyektni yaratamiz (Hozircha branch/org'siz)
#         instance = StudentGroup(**validated_data)
#
#         if group:
#             # 2. Group'dan obyektlarni olamiz
#             branch_obj = getattr(group, 'branch', None)
#             org_obj = getattr(group, 'organization', None)
#
#             # 3. Ularni ID orqali bog'laymiz (Xatolikni oldini olish uchun eng xavfsiz yo'l)
#             if branch_obj:
#                 instance.branch_id = branch_obj.id  # Obyektni o'zi emas, ID'si!
#             if org_obj:
#                 instance.organization_id = org_obj.id # Obyektni o'zi emas, ID'si!
#
#         # 4. Endi saqlaymiz
#         instance.save()
#         return instance
#
#
# class StudentFreezeDetailSerializer(serializers.ModelSerializer):
#     """Muzlatish batafsil ma'lumot"""
#     student = StudentMinimalSerializer()
#     group = GroupMinimalSerializer()
#     created_by = serializers.StringRelatedField()
#
#     class Meta:
#         model = StudentFreezes
#         fields = '__all__'
#
#
# from rest_framework import serializers
# from .models import Group, GroupTeacher, Course, Room, LessonSchedule
# from .models import StudentGroup, Student
# from accounts.models import Employee
#
#
#
#
#
# class CourseMinimalSerializer(serializers.ModelSerializer):
#     """Kurs minimal ma'lumot"""
#
#     class Meta:
#         model = Course
#         fields = '__all__'
#
#
# class TeacherMinimalSerializer(serializers.ModelSerializer):
#     """O'qituvchi minimal ma'lumot"""
#     full_name = serializers.SerializerMethodField()
#
#     class Meta:
#         model = Employee
#         fields = '__all__'
#
#     def get_full_name(self, obj):
#         return f"{obj.first_name} {obj.last_name}"
#
#
#
#
#
#
# class GroupCreateSerializer(serializers.ModelSerializer):
#     """Guruh yaratish"""
#     course_id = serializers.UUIDField(write_only=True)
#     room_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
#     teacher_ids = serializers.ListField(
#         child=serializers.UUIDField(),
#         write_only=True,
#         required=False
#     )
#
#     class Meta:
#         model = Group
#         fields = '__all__'
#         read_only_fields = ['id']
#
#     def validate(self, data):
#         # Kurs tekshirish
#         try:
#             course = Course.objects.get(id=data['course_id'])
#             data['course'] = course
#         except Course.DoesNotExist:
#             raise serializers.ValidationError("Kurs topilmadi")
#
#         # Xona tekshirish
#         if data.get('room_id'):
#             try:
#                 room = Room.objects.get(id=data['room_id'])
#                 data['room'] = room
#             except Room.DoesNotExist:
#                 raise serializers.ValidationError("Xona topilmadi")
#
#         # Sanalarni tekshirish
#         if data['end_date'] <= data['start_date']:
#             raise serializers.ValidationError(
#                 "Tugash sanasi boshlanish sanasidan katta bo'lishi kerak"
#             )
#
#         return data
#
#     def create(self, validated_data):
#         course = validated_data.pop('course')
#         room = validated_data.pop('room', None)
#         teacher_ids = validated_data.pop('teacher_ids', [])
#         validated_data.pop('course_id')
#         validated_data.pop('room_id', None)
#
#         # Guruh yaratish
#         group = Group.objects.create(
#             course=course,
#             room=room,
#             **validated_data
#         )
#
#         # O'qituvchilarni qo'shish
#         for teacher_id in teacher_ids:
#             try:
#                 teacher = Employee.objects.get(id=teacher_id, role='teacher')
#                 GroupTeacher.objects.create(
#                     group=group,
#                     teacher=teacher,
#                     start_date=group.start_date,
#                     end_date=group.end_date
#                 )
#             except Employee.DoesNotExist:
#                 pass
#
#         return group
#
#
# class GroupUpdateSerializer(serializers.ModelSerializer):
#     """Guruhni tahrirlash"""
#     course_id = serializers.UUIDField(required=False)
#     room_id = serializers.UUIDField(required=False, allow_null=True)
#
#     class Meta:
#         model = Group
#         fields = '__all__'
#         read_only_fields = ['id']
#
#     def update(self, instance, validated_data):
#         # Kurs yangilash
#         if 'course_id' in validated_data:
#             try:
#                 course = Course.objects.get(id=validated_data.pop('course_id'))
#                 instance.course = course
#             except Course.DoesNotExist:
#                 pass
#
#         # Xona yangilash
#         if 'room_id' in validated_data:
#             room_id = validated_data.pop('room_id')
#             if room_id:
#                 try:
#                     room = Room.objects.get(id=room_id)
#                     instance.room = room
#                 except Room.DoesNotExist:
#                     pass
#             else:
#                 instance.room = None
#
#         # Qolgan fieldlarni yangilash
#         for attr, value in validated_data.items():
#             setattr(instance, attr, value)
#
#         instance.save()
#         return instance
#
#
#
#
#
# class GroupArchiveSerializer(serializers.Serializer):
#     """Guruhni arxivlash"""
#     reason = serializers.CharField(required=False, allow_blank=True)
#
#
# class GroupFilterSerializer(serializers.Serializer):
#     """Filter parametrlari"""
#     status = serializers.ChoiceField(
#         choices=['active', 'expired', 'archived'],
#         required=False
#     )
#     course_id = serializers.UUIDField(required=False)
#     teacher_id = serializers.UUIDField(required=False)
#     room_id = serializers.UUIDField(required=False)
#     search = serializers.CharField(required=False)
#     start_date_from = serializers.DateField(required=False)
#     start_date_to = serializers.DateField(required=False)
#     has_students = serializers.BooleanField(required=False)
#     days_until_end_lt = serializers.IntegerField(required=False)
#
#
# # expor qilishh guruh malumotlarini hammasini
#
#
# class GroupExportFilterSerializer(serializers.Serializer):
#     """Guruhlar export uchun filter"""
#     group_ids = serializers.ListField(
#         child=serializers.UUIDField(),
#         required=False,
#         help_text="Aniq guruhlar (bo'sh bo'lsa - barcha guruhlar)"
#     )
#     status = serializers.ChoiceField(
#         choices=['active', 'expired', 'archived'],
#         required=False
#     )
#     course_id = serializers.UUIDField(required=False)
#     teacher_id = serializers.UUIDField(required=False)
#     room_id = serializers.UUIDField(required=False)
#     start_date_from = serializers.DateField(required=False)
#     start_date_to = serializers.DateField(required=False)
#
#
# class GroupExportColumnsSerializer(serializers.Serializer):
#     """Export qilinadigan ustunlar"""
#     # Default columns (har doim export qilinadi)
#     default_columns = serializers.ListField(
#         child=serializers.CharField(),
#         default=[
#             'group_id', 'group_name', 'course_name', 'status',
#             'teacher_names', 'room_name', 'start_date', 'end_date',
#             'students_count', 'created_at'
#         ]
#     )
#
#     # Qo'shimcha ustunlar (user tanlaydi)
#     additional_columns = serializers.ListField(
#         child=serializers.ChoiceField(choices=[
#             'course_code',
#             'course_price',
#             'lesson_month',
#             'room_capacity',
#             'lesson_schedule',
#             'active_students',
#             'left_students',
#             'frozen_students',
#             'trial_students',
#             'total_revenue',
#             'expected_revenue',
#             'days_until_end',
#             'progress_percentage',
#             'total_lessons',
#             'completed_lessons',
#             'attendance_rate',
#         ]),
#         required=False,
#         default=[]
#     )
#
#
# class StudentExportFilterSerializer(serializers.Serializer):
#     """Talabalar export uchun filter"""
#     group_id = serializers.UUIDField(required=True)
#     student_types = serializers.ListField(
#         child=serializers.ChoiceField(choices=[
#             'active',  # Faol talabalar
#             'trial',  # Sinov darslari
#             'frozen',  # Muzlatilgan
#             'left'  # Ketgan
#         ]),
#         default=['active']
#     )
#
#
# class StudentExportColumnsSerializer(serializers.Serializer):
#     """Talabalar export ustunlari"""
#     default_columns = serializers.ListField(
#         child=serializers.CharField(),
#         default=[
#             'student_id', 'full_name', 'phone_number', 'joined_at',
#             'status', 'balance'
#         ]
#     )
#
#     additional_columns = serializers.ListField(
#         child=serializers.ChoiceField(choices=[
#             'phone_number2',
#             'parent_name',
#             'parent_phone',
#             'email',
#             'telegram_username',
#             'address',
#             'group_name',
#             'course_name',
#             'teacher_name',
#             'room_name',
#             'start_date',
#             'end_date',
#             'left_at',
#             'leave_reason',
#             'total_paid',
#             'total_debt',
#             'freeze_days',
#             'attendance_count',
#             'absence_count',
#             'attendance_rate',
#             'last_payment_date',
#             'last_payment_amount',
#         ]),
#         required=False,
#         default=[]
#     )
#
#
# class ExportHistorySerializer(serializers.ModelSerializer):
#     """Export tarixi (AuditLog dan)"""
#     performed_by = serializers.SerializerMethodField()
#     export_info = serializers.SerializerMethodField()
#
#     class Meta:
#         model = AuditLog
#         fields = '__all__'
#
#     def get_performed_by(self, obj):
#         if obj.performed_by:
#             return {
#                 'id': str(obj.performed_by.id),
#                 'name': f"{obj.performed_by.first_name} {obj.performed_by.last_name}",
#                 'role': obj.performed_by_role
#             }
#         return None
#
#     def get_export_info(self, obj):
#         """Export ma'lumotlari (new_action fielddan)"""
#         if obj.new_action:
#             return {
#                 'export_type': obj.new_action.get('export_type'),
#                 'file_name': obj.new_action.get('file_name'),
#                 'total_records': obj.new_action.get('total_records'),
#                 'columns_count': obj.new_action.get('columns_count'),
#                 'filters': obj.new_action.get('filters')
#             }
#         return None
#
#
# def create_export_audit_log(user, export_type, file_name, total_records, columns, filters=None):
#     """Export audit log yaratish"""
#     AuditLog.objects.create(
#         entity_type=AuditEntityType.OTHER,
#         entity_id=None,  # Export uchun ID yo'q
#         action=AuditAction.CREATE,
#         old_data=None,
#         new_action={
#             'export_type': export_type,  # 'groups' yoki 'students'
#             'file_name': file_name,
#             'total_records': total_records,
#             'columns_count': len(columns),
#             'filters': filters,
#             'exported_at': datetime.now().isoformat()
#         },
#         performed_by=user,
#         performed_by_role=user.role if hasattr(user, 'role') else 'unknown'
#     )
#
#
# class GroupExportDataSerializer(serializers.Serializer):
#     """Guruh export ma'lumotlari"""
#
#     def to_representation(self, group):
#         """Guruh ma'lumotlarini export formatida qaytarish"""
#         columns = self.context.get('columns', [])
#         data = {}
#
#         # Default columns
#         if 'group_id' in columns:
#             data['Guruh ID'] = str(group.id)
#
#         if 'group_name' in columns:
#             data['Guruh nomi'] = group.name
#
#         if 'course_name' in columns:
#             data['Kurs nomi'] = group.course.name if group.course else ''
#
#         if 'status' in columns:
#             data['Status'] = group.get_status_display()
#
#         if 'teacher_names' in columns:
#             teachers = GroupTeacher.objects.filter(
#                 group=group,
#                 end_date__isnull=True
#             ).select_related('teacher')
#             data["O'qituvchilar"] = ', '.join([
#                 f"{t.teacher.first_name} {t.teacher.last_name}"
#                 for t in teachers
#             ])
#
#         if 'room_name' in columns:
#             data['Xona'] = group.room.name if group.room else ''
#
#         if 'start_date' in columns:
#             data['Boshlanish sanasi'] = group.start_date.strftime('%d.%m.%Y') if group.start_date else ''
#
#         if 'end_date' in columns:
#             data['Tugash sanasi'] = group.end_date.strftime('%d.%m.%Y') if group.end_date else ''
#
#         if 'students_count' in columns:
#             data['Talabalar soni'] = StudentGroup.objects.filter(
#                 group=group,
#                 left_at__isnull=True
#             ).count()
#
#         if 'created_at' in columns:
#             data['Yaratilgan'] = group.created_at.strftime('%d.%m.%Y %H:%M')
#
#         # Additional columns
#         if 'course_code' in columns:
#             data['Kurs kodi'] = group.course.code if group.course else ''
#
#         if 'course_price' in columns:
#             data['Kurs narxi'] = str(group.course.monthly_price) if group.course else ''
#
#         if 'lesson_month' in columns:
#             data['Darslar soni (oy)'] = group.course.lesson_month if group.course else ''
#
#         if 'room_capacity' in columns:
#             data['Xona sig\'imi'] = group.room.capacity if group.room else ''
#
#         if 'lesson_schedule' in columns:
#             schedules = LessonSchedule.objects.filter(group=group)
#             schedule_str = ', '.join([
#                 f"{s.get_day_type_display()}: {s.start_time.strftime('%H:%M')}-{s.end_time.strftime('%H:%M')}"
#                 for s in schedules
#             ])
#             data['Dars jadvali'] = schedule_str
#
#         if 'active_students' in columns:
#             data['Faol talabalar'] = StudentGroup.objects.filter(
#                 group=group,
#                 left_at__isnull=True
#             ).count()
#
#         if 'left_students' in columns:
#             data['Ketgan talabalar'] = StudentGroup.objects.filter(
#                 group=group,
#                 left_at__isnull=False
#             ).count()
#
#         if 'frozen_students' in columns:
#             data['Muzlatilgan talabalar'] = StudentFreezes.objects.filter(
#                 group=group,
#                 freeze_end_date__gte=datetime.now().date()
#             ).count()
#
#         if 'days_until_end' in columns:
#             if group.end_date:
#                 delta = (group.end_date - datetime.now().date()).days
#                 data['Tugashigacha (kun)'] = max(0, delta)
#
#         if 'progress_percentage' in columns:
#             if group.start_date and group.end_date:
#                 total = (group.end_date - group.start_date).days
#                 passed = (datetime.now().date() - group.start_date).days
#                 data['Progress (%)'] = min(round((passed / total) * 100, 1), 100) if total > 0 else 0
#
#         return data
#
#
# class StudentExportDataSerializer(serializers.Serializer):
#     """Talaba export ma'lumotlari"""
#
#     def to_representation(self, student_group):
#         """Talaba ma'lumotlarini export formatida qaytarish"""
#         columns = self.context.get('columns', [])
#         student = student_group.student
#         data = {}
#
#         # Default columns
#         if 'student_id' in columns:
#             data['Talaba ID'] = str(student.id)
#
#         if 'full_name' in columns:
#             data['To\'liq ismi'] = student.full_name
#
#         if 'phone_number' in columns:
#             data['Telefon'] = student.phone_number
#
#         if 'joined_at' in columns:
#             data['Qo\'shilgan sana'] = student_group.joined_at.strftime('%d.%m.%Y') if student_group.joined_at else ''
#
#         if 'status' in columns:
#             if student_group.left_at:
#                 data['Status'] = 'Ketgan'
#             else:
#                 # Muzlatilganmi tekshirish
#                 is_frozen = StudentFreezes.objects.filter(
#                     student=student,
#                     group=student_group.group,
#                     freeze_end_date__gte=datetime.now().date()
#                 ).exists()
#                 data['Status'] = 'Muzlatilgan' if is_frozen else 'Faol'
#
#         # Additional columns
#         if 'phone_number2' in columns:
#             data['Telefon 2'] = student.phone_number2 or ''
#
#         if 'parent_name' in columns:
#             data['Ota-ona'] = student.parent_name or ''
#
#         if 'parent_phone' in columns:
#             data['Ota-ona tel.'] = student.parent_phone or ''
#
#         if 'email' in columns:
#             data['Email'] = student.email or ''
#
#         if 'telegram_username' in columns:
#             data['Telegram'] = student.telegram_username or ''
#
#         if 'address' in columns:
#             data['Manzil'] = student.address or ''
#
#         if 'group_name' in columns:
#             data['Guruh'] = student_group.group.name
#
#         if 'course_name' in columns:
#             data['Kurs'] = student_group.group.course.name if student_group.group.course else ''
#
#         if 'left_at' in columns:
#             data['Ketgan sana'] = student_group.left_at.strftime('%d.%m.%Y') if student_group.left_at else ''
#
#         if 'attendance_count' in columns:
#             data['Keldi (kun)'] = Attendence.objects.filter(
#                 student_group=student_group,
#                 is_present=True
#             ).count()
#
#         if 'absence_count' in columns:
#             data['Kelmadi (kun)'] = Attendence.objects.filter(
#                 student_group=student_group,
#                 is_present=False
#             ).count()
#
#         return data
#
#
# #   imtihon yaratish api  ///////////////////////////////////////////////////////////
#
#
# class ExamCreateSerializer(serializers.ModelSerializer):
#     """Imtihon yaratish"""
#     group_id = serializers.UUIDField(write_only=True)
#
#     class Meta:
#         model = Exams
#         fields = [
#             'id', 'group_id', 'title', 'exam_date', 'min_score',
#             'max_score', 'description', 'file'
#         ]
#         read_only_fields = ['id']
#
#     def validate(self, data):
#         # Guruh tekshirish
#         try:
#             group = Group.objects.get(id=data['group_id'])
#             data['group'] = group
#         except Group.DoesNotExist:
#             raise serializers.ValidationError("Guruh topilmadi")
#
#         # Ballar tekshirish
#         if data['min_score'] >= data['max_score']:
#             raise serializers.ValidationError(
#                 "O'tish bali maksimal baldan kichik bo'lishi kerak"
#             )
#
#         if data['min_score'] < 0 or data['max_score'] < 0:
#             raise serializers.ValidationError(
#                 "Ballar musbat bo'lishi kerak"
#             )
#
#         return data
#
#     def create(self, validated_data):
#         group = validated_data.pop('group')
#         validated_data.pop('group_id', None)
#         created_by = validated_data.pop('created_by', None)
#
#         # Imtihonni yaratish
#         exam = Exams.objects.create(
#             group=group,
#             # Modelda maydonlar 'branch_id' va 'organization_id' deb nomlangan
#             # Shuning uchun ularga to'g'ridan-to'g'ri ID qiymatini beramiz
#             branch_id_id=group.branch_id,
#             organization_id_id=group.organization_id,
#             created_by=created_by,
#             **validated_data
#         )
#
#         return exam
#
#
# class ExamUpdateSerializer(serializers.ModelSerializer):
#     """Imtihonni tahrirlash"""
#
#     class Meta:
#         model = Exams
#         fields = '__all__'
#         read_only_fields = ['id']
#
#     def validate(self, data):
#         # Ballar tekshirish
#         min_score = data.get('min_score', self.instance.min_score)
#         max_score = data.get('max_score', self.instance.max_score)
#
#         if min_score >= max_score:
#             raise serializers.ValidationError(
#                 "O'tish bali maksimal baldan kichik bo'lishi kerak"
#             )
#
#         return data
#
#
#
#
#
# class ExamResultSerializer(serializers.ModelSerializer):
#     """Imtihon natijasini kiritish/tahrirlash"""
#     student_id = serializers.UUIDField(write_only=True)
#     exam_id = serializers.UUIDField(write_only=True)
#
#     class Meta:
#         model = ExamResults
#         fields = '__all__'
#         read_only_fields = ['id']
#
#     def validate(self, data):
#         # Exam tekshirish
#         try:
#             exam = Exams.objects.get(id=data['exam_id'])
#             data['exam'] = exam
#         except Exams.DoesNotExist:
#             raise serializers.ValidationError("Imtihon topilmadi")
#
#         # Student tekshirish
#         try:
#             student = Student.objects.get(id=data['student_id'])
#             data['student'] = student
#         except Student.DoesNotExist:
#             raise serializers.ValidationError("Talaba topilmadi")
#
#         # Ball tekshirish
#         if data['score'] < 0 or data['score'] > exam.max_score:
#             raise serializers.ValidationError(
#                 f"Ball 0 dan {exam.max_score} gacha bo'lishi kerak"
#             )
#
#         return data
#
#     def create(self, validated_data):
#         exam = validated_data.pop('exam')
#         student = validated_data.pop('student')
#         validated_data.pop('exam_id')
#         validated_data.pop('student_id')
#
#         # ExamResult yaratish yoki yangilash
#         result, created = ExamResults.objects.update_or_create(
#             exam=exam,
#             student=student,
#             defaults={
#                 'score': validated_data['score'],
#                 'comment': validated_data.get('comment', ''),
#                 'created_by': self.context['request'].user
#             }
#         )
#
#         return result
#
#
# class ExamResultDetailSerializer(serializers.ModelSerializer):
#     """Imtihon natijasi batafsil"""
#     student = StudentMinimalSerializer()
#     status = serializers.SerializerMethodField()
#     status_color = serializers.SerializerMethodField()
#     created_by = serializers.SerializerMethodField()
#
#     class Meta:
#         model = ExamResults
#         fields = '__all__'
#
#     def get_status(self, obj):
#         """Imtihon holati"""
#         if obj.score >= obj.exam.min_score:
#             return 'passed'  # O'tdi
#         else:
#             return 'failed'  # O'tmadi
#
#     def get_status_color(self, obj):
#         """Status rangi"""
#         if obj.score >= obj.exam.min_score:
#             return 'green'  # Yashil - o'tdi
#         else:
#             return 'red'  # Qizil - o'tmadi
#
#     def get_created_by(self, obj):
#         if obj.created_by:
#             return {
#                 'id': str(obj.created_by.id),
#                 'name': f"{obj.created_by.first_name} {obj.created_by.last_name}"
#             }
#         return None
#
#
# class ExamListSerializer(serializers.ModelSerializer):
#     """Imtihonlar ro'yxati"""
#     group_name = serializers.CharField(source='group.name', read_only=True)
#     total_students = serializers.SerializerMethodField()
#     graded_students = serializers.SerializerMethodField()
#     passed_students = serializers.SerializerMethodField()
#     created_by = serializers.SerializerMethodField()
#
#     class Meta:
#         model = Exams
#         fields = '__all__'
#
#     def get_total_students(self, obj):
#         """Jami talabalar soni (qatnashishga haqli)"""
#         # Bu sozlamalardan kelib chiqadi (faol, sinov, va h.k.)
#         return self._get_eligible_students(obj).count()
#
#     def get_graded_students(self, obj):
#         """Baholangan talabalar"""
#         return ExamResults.objects.filter(exam=obj).count()
#
#     def get_passed_students(self, obj):
#         """O'tgan talabalar"""
#         return ExamResults.objects.filter(
#             exam=obj,
#             score__gte=obj.min_score
#         ).count()
#
#     def get_created_by(self, obj):
#         if obj.created_by:
#             return f"{obj.created_by.first_name} {obj.created_by.last_name}"
#         return None
#
#     def _get_eligible_students(self, exam):
#         """Imtihonga qatnashishga haqli talabalar"""
#         # Sozlamalardan kelib chiqadi
#         # Hozircha faqat faol talabalarni qaytaramiz
#         return StudentGroup.objects.filter(
#             group=exam.group,
#             left_at__isnull=True
#         )
#
#
# class ExamDetailSerializer(serializers.ModelSerializer):
#     """Imtihon batafsil ma'lumot"""
#     group = serializers.SerializerMethodField()
#     created_by = serializers.SerializerMethodField()
#     results = serializers.SerializerMethodField()
#     statistics = serializers.SerializerMethodField()
#
#     class Meta:
#         model = Exams
#         fields = '__all__'
#
#     def get_group(self, obj):
#         return {
#             'id': str(obj.group.id),
#             'name': obj.group.name
#         }
#
#     def get_created_by(self, obj):
#         if obj.created_by and obj.created_by.user:
#             return {
#                 'id': str(obj.created_by.id),
#                 # Employee orqali uning User'iga o'tib, ism-familiyasini olamiz
#                 'name': f"{obj.created_by.user.first_name} {obj.created_by.user.last_name}"
#             }
#         return None
#
#     def get_results(self, obj):
#         """Talabalar natijalari"""
#         # Barcha haqli talabalarni olish
#         eligible_students = StudentGroup.objects.filter(
#             group=obj.group,
#             left_at__isnull=True
#         ).select_related('student')
#
#         results = []
#         for student_group in eligible_students:
#             student = student_group.student
#
#             # Natija bormi tekshirish
#             try:
#                 exam_result = ExamResults.objects.get(
#                     exam=obj,
#                     student=student
#                 )
#                 results.append({
#                     'student': StudentMinimalSerializer(student).data,
#                     'score': exam_result.score,
#                     'comment': exam_result.comment,
#                     'status': 'passed' if exam_result.score >= obj.min_score else 'failed',
#                     'status_color': 'green' if exam_result.score >= obj.min_score else 'red',
#                     'graded': True
#                 })
#             except ExamResults.DoesNotExist:
#                 # Baholanmagan
#                 results.append({
#                     'student': StudentMinimalSerializer(student).data,
#                     'score': None,
#                     'comment': '',
#                     'status': 'not_graded',
#                     'status_color': 'gray',  # Sabzirang (kulrang)
#                     'graded': False
#                 })
#
#         return results
#
#     def get_statistics(self, obj):
#         """Statistika"""
#         total = StudentGroup.objects.filter(
#             group=obj.group,
#             left_at__isnull=True
#         ).count()
#
#         results = ExamResults.objects.filter(exam=obj)
#         graded = results.count()
#         passed = results.filter(score__gte=obj.min_score).count()
#         failed = results.filter(score__lt=obj.min_score).count()
#         not_graded = total - graded
#
#         # O'rtacha ball
#         avg_score = results.aggregate(
#             avg=serializers.models.Avg('score')
#         )['avg'] or 0
#
#         return {
#             'total_students': total,
#             'graded': graded,
#             'not_graded': not_graded,
#             'passed': passed,
#             'failed': failed,
#             'average_score': round(float(avg_score), 2),
#             'pass_rate': round((passed / graded * 100), 1) if graded > 0 else 0
#         }
#
#
# class ExamParticipantsSettingsSerializer(serializers.Serializer):
#     """Imtihon qatnashuvchilar sozlamalari (faqat CEO uchun)"""
#     include_active = serializers.BooleanField(default=True)
#     include_trial = serializers.BooleanField(default=False)
#     include_frozen = serializers.BooleanField(default=False)
#     include_left = serializers.BooleanField(default=False)
#
# # dars mavzusini belgilash
# class OnlineLessonCreateSerializer(serializers.ModelSerializer):
#     """Onlayn dars yaratish"""
#     group_id = serializers.UUIDField(write_only=True)
#
#     class Meta:
#         model = OnlineLesson
#         fields = '__all__'
#         read_only_fields = ['id']
#
#     def validate(self, data):
#         # Guruh tekshirish
#         try:
#             group = Group.objects.get(id=data['group_id'])
#             data['group'] = group
#         except Group.DoesNotExist:
#             raise serializers.ValidationError("Guruh topilmadi")
#
#         # Content type ga qarab kerakli fieldlarni tekshirish
#         content_type = data.get('content_type')
#
#         if content_type == 'video' and not data.get('video_url'):
#             raise serializers.ValidationError("Video uchun URL kerak")
#
#         if content_type == 'document' and not data.get('file'):
#             raise serializers.ValidationError("Hujjat uchun fayl kerak")
#
#         if content_type == 'link' and not data.get('external_link'):
#             raise serializers.ValidationError("Havola uchun URL kerak")
#
#         if content_type == 'text' and not data.get('text_content'):
#             raise serializers.ValidationError("Matn uchun kontent kerak")
#
#         return data
#
#     def create(self, validated_data):
#         group = validated_data.pop('group')
#         validated_data.pop('group_id')
#
#         # Dars yaratish
#         lesson = OnlineLesson.objects.create(
#             group=group,
#             created_by=self.context['request'].user,
#             **validated_data
#         )
#
#         return lesson
#
#
# class OnlineLessonUpdateSerializer(serializers.ModelSerializer):
#     """Onlayn darsni tahrirlash"""
#
#     class Meta:
#         model = OnlineLesson
#         fields = '__all__'
#         read_only_fields = ['id']
#
#
#
#
#
# class LessonTopicSerializer(serializers.Serializer):
#     """Dars mavzusi belgilash"""
#     group_id = serializers.UUIDField()
#     lesson_date = serializers.DateField()
#     title = serializers.CharField(max_length=250)
#     description = serializers.CharField(required=False, allow_blank=True)
#
#     def validate(self, data):
#         # Guruh tekshirish
#         try:
#             group = Group.objects.get(id=data['group_id'])
#             data['group'] = group
#         except Group.DoesNotExist:
#             raise serializers.ValidationError("Guruh topilmadi")
#
#         return data
#
#     def create(self, validated_data):
#         """Mavzu belgilanganda avtomatik onlayn dars yaratish"""
#         group = validated_data['group']
#         lesson_date = validated_data['lesson_date']
#         title = validated_data['title']
#         description = validated_data.get('description', '')
#
#         # Onlayn dars yaratish (bo'sh kontent bilan)
#         lesson = OnlineLesson.objects.create(
#             group=group,
#             title=title,
#             description=description,
#             content_type='text',  # Default
#             lesson_date=lesson_date,
#             is_published=False,
#             created_by=self.context['request'].user
#         )
#
#         return lesson
#
#
# class GroupLessonsCalendarSerializer(serializers.Serializer):
#     """Guruh dars kalendari"""
#     group_id = serializers.UUIDField()
#     start_date = serializers.DateField(required=False)
#     end_date = serializers.DateField(required=False)
#
#     def validate(self, data):
#         # Guruh tekshirish
#         try:
#             group = Group.objects.get(id=data['group_id'])
#             data['group'] = group
#         except Group.DoesNotExist:
#             raise serializers.ValidationError("Guruh topilmadi")
#
#         # Default sanalar
#         if 'start_date' not in data:
#             data['start_date'] = group.start_date
#         if 'end_date' not in data:
#             data['end_date'] = group.end_date
#
#         return data
#
#
# class BulkLessonTopicSerializer(serializers.Serializer):
#     """Ko'p darsga mavzu belgilash (yillik/oylik reja)"""
#     group_id = serializers.UUIDField()
#     topics = serializers.ListField(
#         child=serializers.DictField(),
#         min_length=1
#     )
#
#     def validate(self, data):
#         # Guruh tekshirish
#         try:
#             group = Group.objects.get(id=data['group_id'])
#             data['group'] = group
#         except Group.DoesNotExist:
#             raise serializers.ValidationError("Guruh topilmadi")
#
#         # Har bir mavzuni tekshirish
#         for topic in data['topics']:
#             if 'lesson_date' not in topic or 'title' not in topic:
#                 raise serializers.ValidationError(
#                     "Har bir mavzuda lesson_date va title bo'lishi kerak"
#                 )
#
#         return data
#
#     def create(self, validated_data):
#         """Ko'p darsga mavzu belgilash"""
#         group = validated_data['group']
#         topics = validated_data['topics']
#
#         created_lessons = []
#
#         for topic in topics:
#             lesson = OnlineLesson.objects.create(
#                 group=group,
#                 title=topic['title'],
#                 description=topic.get('description', ''),
#                 content_type='text',
#                 lesson_date=topic['lesson_date'],
#                 is_published=False,
#                 order=topic.get('order', 0),
#                 created_by=self.context['request'].user
#             )
#             created_lessons.append(lesson)
#
#         return created_lessons
#
#
#
# from rest_framework import serializers
# from .models.student import (
#     Student, StudentGroup, StudentBalances, StudentTarnsactions,
#     StudentFreezes, StudentBalanceHistory
# )
# from .models.group import Group, GroupTeacher, Course
# from accounts.models import Employee
#
#
#
# # ──────────────────────────────────────────
# # YANGI TALABA YARATISH  (2-3-rasm)
# # ──────────────────────────────────────────
# import re # Tepaga qo'shib qo'ying
#
# class StudentCreateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Student
#         fields = '__all__'
#
#     def validate_phone_number(self, value):
#         # 1. Faqat raqamlarni ajratib olamiz (+998 20... -> 99820...)
#         clean_number = re.sub(r'\D', '', value)
#
#         # 2. Uzunligini tekshiramiz (9 talik yoki 12 talik bo'lishi mumkin)
#         if len(clean_number) < 9:
#             raise serializers.ValidationError("Telefon raqami juda qisqa.")
#
#         # 3. Bazada borligini tekshirishda ham tozalangan raqamni ishlating
#         # (Agar bazada raqamlar har xil formatda saqlangan bo'lsa, bu muhim)
#         if Student.objects.filter(phone_number__icontains=clean_number).exists():
#              raise serializers.ValidationError("Bu telefon raqam allaqachon mavjud.")
#
#         return value
#
#
#
# class StudentUpdateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Student
#         fields = '__all__'
#
#     def validate_phone_number(self, value):
#         # Raqamni tozalash
#         clean_number = re.sub(r'\D', '', value)
#
#         if len(clean_number) < 9:
#             raise serializers.ValidationError("Telefon raqami noto'g'ri.")
#
#         # O'zidan tashqari boshqalarda borligini tekshirish
#         if Student.objects.filter(phone_number__icontains=clean_number).exclude(pk=self.instance.pk).exists():
#             raise serializers.ValidationError("Bu telefon raqam allaqachon mavjud.")
#
#         return value
#
#
#
# # ──────────────────────────────────────────
# # TRANZAKSIYA (to'lov tarixi)
# # ──────────────────────────────────────────
#
# class TransactionSerializer(serializers.ModelSerializer):
#     # 1. Talaba ismini chiqarish (Rasmda "Ismi kiritilmagan" bo'lib turibdi)
#     student_name = serializers.CharField(source='student.full_name', read_only=True)
#
#     # 2. To'lovni qabul qilgan xodim ismi
#     accepted_by_name = serializers.SerializerMethodField()
#
#     # 3. Agar modelda o'qituvchi bog'langan bo'lsa (bo'sh qolmasligi uchun)
#     teacher_name = serializers.SerializerMethodField()
#
#     class Meta:
#         model  = StudentTarnsactions
#         fields = [
#             'id', 'student', 'student_name', 'amount',
#             'transaction_type', 'payment_type', 'transaction_date',
#             'comment', 'accepted_by_name', 'teacher_name'
#         ]
#
#     def get_accepted_by_name(self, obj):
#         if obj.accepted_by and obj.accepted_by.user:
#             user = obj.accepted_by.user
#             full_name = f"{user.first_name} {user.last_name}".strip()
#             return full_name if full_name else user.email
#         return "-"
#
#     def get_teacher_name(self, obj):
#         if hasattr(obj, 'teacher') and obj.teacher:
#             return obj.teacher.user.full_name
#         return "-"
#
#
# class StudentDetailSerializer(serializers.ModelSerializer):
#     balance      = serializers.SerializerMethodField()
#     status       = serializers.SerializerMethodField()
#     groups       = serializers.SerializerMethodField()
#     transactions = serializers.SerializerMethodField()
#     branch_name  = serializers.SerializerMethodField()
#
#     class Meta:
#         model  = Student
#         fields = '__all__'
#
#     def get_balance(self, obj):
#         b = obj.student_balances.first()
#         return float(b.balance) if b else 0
#
#     def get_status(self, obj):
#         active_sg = obj.studentgroup_student.filter(left_at__isnull=True).first()
#         if not active_sg:
#             return {'code': 'inactive', 'label': 'Faol emas'}
#         freeze = obj.studentfreezes_student.filter(freeze_end_date__isnull=True).first()
#         if freeze:
#             return {'code': 'frozen', 'label': 'Muzlatilgan'}
#         return {'code': 'active', 'label': 'Faol'}
#
#     def get_groups(self, obj):
#         sgs = obj.studentgroup_student.select_related('group__course').all()
#         return StudentGroupDetailSerializer(sgs, many=True).data
#
#     def get_transactions(self, obj):
#         txns = obj.student_transactions.order_by('-transaction_date')[:20]
#         return TransactionSerializer(txns, many=True).data
#
#     def get_branch_name(self, obj):
#         if hasattr(obj, 'branch_id') and obj.branch_id:
#             return obj.branch_id.name
#         return None
#     active_groups = serializers.SerializerMethodField()
#     recent_payments = serializers.SerializerMethodField()
#
#
#     def get_active_groups(self, obj):
#         groups = obj.Sgroup_student.filter(left_at__isnull=True)
#         return [{"group_name": g.group.name, "joined_at": g.joined_at} for g in groups]
#
#     def get_recent_payments(self, obj):
#         payments = obj.Strans_student.filter(transaction_type='payment').order_by('-transaction_date')[:5]
#         return [{"amount": float(p.amount), "date": p.transaction_date} for p in payments]
#
#
# # academics/serializers.py
# from rest_framework import serializers
# from .models import Group, Student, StudentGroup, StudentPricing, Exams, Attendence
# from .models.lesson import OnlineLesson
#
#
# # 8. Davomat ro'yxati uchun
# class AttendanceListSerializer(serializers.Serializer):
#     student_group_id = serializers.UUIDField()
#     student_name = serializers.CharField()
#     phone = serializers.CharField()
#     is_present = serializers.BooleanField(allow_null=True)
#     marked_at = serializers.DateTimeField(allow_null=True)
#
#
#
#
#
