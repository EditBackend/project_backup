from django.urls import path, include
from rest_framework.routers import DefaultRouter

# ════════════════════════════════════════════════════════════════
#  IMPORTLAR (Kategoriyalar bo'yicha toza import qilinadi)
# ════════════════════════════════════════════════════════════════

# 1. O'qituvchilar (Teacher views)
from academics.views.teacher import (
    TeacherSalaryRulesViewSet, TeacherSalaryPaymentsViewSet,
    TeacherSalaryCalculationsViewSet, GroupTeacherViewSet,
    teachers_list, group_teacher_list_create, group_teacher_detail_update_delete
)

# 2. Guruhlar va Xonalar (Group views)
from academics.views.groups import (
    RoomViewSet, CourseViewSet, course_list, room_list, available_rooms,
    GroupsListView, GroupCreateView, GroupDetailView, GroupArchiveView,
    GroupUnarchiveView, group_full_info, group_statistics, GroupsExportView
)

# 3. Talabalar va To'lovlar (Student views)
from academics.views.student import (
    StudentViewSet, TalabalarMalumotView, StudentAddPaymentView,
    StudentDetailView, StudentTransferView, StudentFreezeView,
    StudentLeaveView, student_search
)

# 4. Darslar, Davomat va Imtihonlar (Lesson views)
from academics.views.lesson import (
    LessonTimeViewSet, LessonScheduleViewSet, AttendenceViewSet,
    GroupAttendanceView, CancelLessonView, ExamsListView,
    ExamCreateView, ExamGradingView, OnlineLessonsListView,
    SetLessonTopicView, PublishLessonView
)


# ════════════════════════════════════════════════════════════════
#  ROUTER (ViewSet'lar uchun avtomatik URL'lar)
# ════════════════════════════════════════════════════════════════
router = DefaultRouter()

# O'qituvchilar uchun
router.register(r'teacher-salary-rules', TeacherSalaryRulesViewSet, basename='teacher-salary-rules')
router.register(r'teacher-salary-payments', TeacherSalaryPaymentsViewSet, basename='teacher-salary-payments')
router.register(r'teacher-salary-calculations', TeacherSalaryCalculationsViewSet, basename='teacher-salary-calculations')
router.register(r'group-teachers', GroupTeacherViewSet, basename='group-teachers')

# Guruh va Kurslar uchun
router.register(r'rooms', RoomViewSet, basename='room')
router.register(r'courses', CourseViewSet, basename='course')

# Talabalar uchun
router.register(r'students', StudentViewSet, basename='student')

# Dars va Davomatlar uchun
router.register(r'lesson-times', LessonTimeViewSet, basename='lesson-time')
router.register(r'lesson-schedules', LessonScheduleViewSet, basename='lesson-schedule')
router.register(r'attendances', AttendenceViewSet, basename='attendance')


# ════════════════════════════════════════════════════════════════
#  URL PATTERNS (APIView va Funksiya ko'rinishidagi View'lar uchun)
# ════════════════════════════════════════════════════════════════

urlpatterns = [
    # 1. Router manzillarini eng tepaga qo'shamiz
    path('', include(router.urls)),

    # ── GURUHLAR (Groups) ─────────────────────────────────────────
    path('groups/list/', GroupsListView.as_view(), name='groups-list'),
    path('groups/create/', GroupCreateView.as_view(), name='groups-create'),
    path('groups/<uuid:pk>/', GroupDetailView.as_view(), name='groups-detail'),
    path('groups/<uuid:group_id>/archive/', GroupArchiveView.as_view(), name='groups-archive'),
    path('groups/<uuid:group_id>/unarchive/', GroupUnarchiveView.as_view(), name='groups-unarchive'),
    path('groups/<uuid:pk>/full-info/', group_full_info, name='groups-full-info'),
    path('groups/statistics/', group_statistics, name='groups-statistics'),
    path('groups/export/', GroupsExportView.as_view(), name='groups-export'),

    # ── O'QITUVCHILAR (Teachers in Groups) ────────────────────────
    path('teachers/list/all/', teachers_list, name='teachers-list-all'),
    path('groups/<uuid:group_pk>/teachers/', group_teacher_list_create, name='group-teacher-list-create'),
    path('groups/<uuid:group_pk>/teachers/<uuid:pk>/', group_teacher_detail_update_delete, name='group-teacher-detail'),

    # ── TALABALAR VA TO'LOVLAR (Students) ─────────────────────────
    path('students/info/', TalabalarMalumotView.as_view(), name='students-info'),
    path('students/search/', student_search, name='students-search'),
    path('students/<uuid:pk>/detail/', StudentDetailView.as_view(), name='students-detail'),
    path('students/<uuid:student_id>/add-payment/', StudentAddPaymentView.as_view(), name='students-add-payment'),
    path('students/transfer/', StudentTransferView.as_view(), name='students-transfer'),
    path('students/freeze/', StudentFreezeView.as_view(), name='students-freeze'),
    path('students/leave/', StudentLeaveView.as_view(), name='students-leave'),

    # ── DARSLAR VA DAVOMAT (Lessons & Attendance) ─────────────────
    path('groups/<uuid:group_id>/attendance/', GroupAttendanceView.as_view(), name='group-attendance'),
    path('groups/<uuid:group_pk>/lessons/<uuid:lesson_pk>/cancel/', CancelLessonView.as_view(), name='cancel-lesson'),

    # ── IMTIHONLAR (Exams) ────────────────────────────────────────
    path('exams/list/', ExamsListView.as_view(), name='exams-list'),
    path('exams/create/', ExamCreateView.as_view(), name='exams-create'),
    path('exams/grading/', ExamGradingView.as_view(), name='exams-grading'),

    # ── ONLAYN DARSLAR (Online Lessons) ───────────────────────────
    path('online-lessons/list/', OnlineLessonsListView.as_view(), name='online-lessons-list'),
    path('online-lessons/set-topic/', SetLessonTopicView.as_view(), name='set-lesson-topic'),
    path('online-lessons/<uuid:lesson_id>/publish/', PublishLessonView.as_view(), name='publish-lesson'),

    # ── YORDAMCHI LUG'ATLAR (Helpers/Dropdowns) ───────────────────
    path('helper/courses/', course_list, name='helper-courses'),
    path('helper/rooms/', room_list, name='helper-rooms'),
    path('helper/available-rooms/', available_rooms, name='helper-available-rooms'),
]