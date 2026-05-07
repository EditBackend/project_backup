from django.urls import path
from .views.groups import GroupViewSet, RoomViewSet, CourseViewSet
from .views.lesson import (LessonScheduleViewSet,
    GroupAttendanceView,
    ExamsViewSet,
    ExamGradingView,
    OnlineLessonViewSet,
    PublishLessonView )
from .views.student import (StudentViewSet,
    TalabalarMalumotView,
    StudentAddPaymentView,
    StudentLeaveFreezeView)
from .views.teacher import (TeacherSalaryRulesViewSet,
    TeacherSalaryCalculationsViewSet,
    TeacherSalaryPaymentsViewSet)

urlpatterns = [
    # --- Groups URLlari ---
    path('groups/', GroupViewSet.as_view({'get': 'list', 'post': 'create'}), name='group-list-create'),
    path('groups/<uuid:pk>/', GroupViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='group-detail'),

    # --- Rooms URLlari ---
    path('rooms/', RoomViewSet.as_view({'get': 'list', 'post': 'create'}), name='room-list-create'),
    path('rooms/<uuid:pk>/', RoomViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='room-detail'),

    # --- Courses URLlari ---
    path('courses/', CourseViewSet.as_view({'get': 'list', 'post': 'create'}), name='course-list-create'),
    path('courses/<uuid:pk>/', CourseViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='course-detail'),






# lesson
    path('schedules/', LessonScheduleViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='schedule-list-create'),

    path('schedules/<uuid:pk>/', LessonScheduleViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='schedule-detail'),

    # 2. Davomat (Attendance) - APIView bo'lgani uchun .as_view() argumentlarsiz
    # Guruh ID bo'yicha davomatni ko'rish va saqlash
    path('attendance/group/<uuid:group_id>/', GroupAttendanceView.as_view(), name='group-attendance'),

    # 3. Imtihonlar (Exams)
    path('exams/', ExamsViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='exam-list-create'),

    path('exams/<uuid:pk>/', ExamsViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='exam-detail'),

    # Imtihon baholarini kiritish (Exam Results)
    path('exams/grading/', ExamGradingView.as_view(), name='exam-grading'),

    # 4. Onlayn darslar (Online Lessons)
    path('online-lessons/', OnlineLessonViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='online-lesson-list-create'),

    path('online-lessons/<uuid:pk>/', OnlineLessonViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='online-lesson-detail'),

    # Darsni e'lon qilish (Publish)
    path('online-lessons/<uuid:lesson_id>/publish/', PublishLessonView.as_view(), name='online-lesson-publish'),




# student
    # 1. Asosiy Talabalar CRUD (ViewSet)
    path('students/', StudentViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='student-list-create'),

    path('students/<uuid:pk>/', StudentViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='student-detail'),

    # 2. Umumiy hisobot (Optimallashtirilgan N+1 yo'q)
    path('students/report/', TalabalarMalumotView.as_view(), name='student-report'),

    # 3. To'lov qabul qilish (Payment)
    path('students/<uuid:student_id>/add-payment/', StudentAddPaymentView.as_view(), name='student-add-payment'),

    # 4. Muzlatish yoki Guruhdan chiqarish (Action orqali boshqariladi)
    # Bu yerda <str:action> 'leave' yoki 'freeze' qiymatlarini qabul qiladi
    path('students/status/<str:action>/', StudentLeaveFreezeView.as_view(), name='student-status-change'),




# teacher
    # 1. O'qituvchi oylik qoidalari (Salary Rules)
    path('teachers/salary-rules/', TeacherSalaryRulesViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='teacher-salary-rules-list'),

    path('teachers/salary-rules/<uuid:pk>/', TeacherSalaryRulesViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='teacher-salary-rules-detail'),

    # 2. Oylik hisob-kitob tabeli (Calculations)
    path('teachers/salary-calculations/', TeacherSalaryCalculationsViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='teacher-salary-calc-list'),

    path('teachers/salary-calculations/<uuid:pk>/', TeacherSalaryCalculationsViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='teacher-salary-calc-detail'),

    # 3. Haqiqiy to'lovlar (Payments)
    path('teachers/salary-payments/', TeacherSalaryPaymentsViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='teacher-salary-payments-list'),

    path('teachers/salary-payments/<uuid:pk>/', TeacherSalaryPaymentsViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='teacher-salary-payments-detail'),

]