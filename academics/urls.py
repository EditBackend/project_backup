from django.urls import path

from .views import (
    StudentViewSet,  StudentPricingViewSet,
    StudentBalancesViewSet, StudentTarnsactionsViewSet, LeaveReasonViewSet,
    StudentGroupLeavesViewSet, StudentFreezesViewSet, StudentBalanceHistoryViewSet,
    AttendenceViewSet, RoomViewSet, CourseViewSet,
    GroupTeacherViewSet, LessonTimeViewSet, LessonScheduleViewSet,
    ExamsViewSet, ExamResultsViewSet, ExamResultsView,
    TeacherSalaryRulesViewSet, TeacherSalaryPaymentsViewSet, TeacherSalaryCalculationsViewSet, GroupHistoryView,
    GroupTeacherHistoryView, GroupStudentsHistoryView, GroupFreezesHistoryView, GroupAuditLogView, StudentTransferView,
    StudentFreezeView, StudentFreezesListView, StudentLeaveView, BalanceRecalculationView, StudentActiveGroupsView,
    GroupArchiveView, GroupUnarchiveView, GroupExportExcelView, GroupStatisticsView, GroupBulkActionView,
    GroupsExportView, StudentsExportView, ExportHistoryView, ExportStatisticsView, ExamsListView, ExamCreateView,
    ExamDetailView, ExamGradingView, ExamStatisticsView, ExamParticipantsSettingsView, OnlineLessonsListView,
    SetLessonTopicView, UpdateLessonTopicView, GroupLessonsCalendarView, BulkSetLessonTopicsView, PublishLessonView,
    LessonStatisticsView, OnlineLessonDetailView,OnlineLessonCreateView,TalabalarMalumotView,GroupDetailUpdateDeleteView,GroupListCreateView,StudentGroupListCreateAPIView, StudentGroupDetailAPIView
)
from . import views
urlpatterns = [
    path('talabalar/', TalabalarMalumotView.as_view(), name='talabalar-list-create'),

    # Bitta talaba uchun (update, delete)
    path('talabalar/<uuid:pk>/', TalabalarMalumotView.as_view(), name='talabalar-detail'),

    # ==================== STUDENT URLs ====================
    path('students/', StudentViewSet.as_view({'get': 'list', 'post': 'create'}), name='student-list'),
    path('students/<uuid:pk>/',
         StudentViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}),
         name='student-detail'),

    # Talabalar va guruhlar ro'yxati
    path('student-groups/', StudentGroupListCreateAPIView.as_view(), name='student-group-list'),

    # ID orqali boshqarish (UUID bo'lsa <uuid:pk>, raqam bo'lsa <uuid:pk>)
    path('student-groups/<uuid:pk>/', StudentGroupDetailAPIView.as_view(), name='student-group-detail'),

    path('student-pricings/', StudentPricingViewSet.as_view({'get': 'list', 'post': 'create'}),
         name='studentpricing-list'),
    path('student-pricings/<uuid:pk>/', StudentPricingViewSet.as_view(
        {'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}),
         name='studentpricing-detail'),

    path('student-balances/', StudentBalancesViewSet.as_view({'get': 'list', 'post': 'create'}),
         name='studentbalances-list'),
    path('student-balances/<uuid:pk>/', StudentBalancesViewSet.as_view(
        {'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}),
         name='studentbalances-detail'),

    path('student-transactions/', StudentTarnsactionsViewSet.as_view({'get': 'list', 'post': 'create'}),
         name='studenttransactions-list'),
    path('student-transactions/<uuid:pk>/', StudentTarnsactionsViewSet.as_view(
        {'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}),
         name='studenttransactions-detail'),

    path('leave-reasons/', LeaveReasonViewSet.as_view({'get': 'list', 'post': 'create'}), name='leavereason-list'),
    path('leave-reasons/<uuid:pk>/', LeaveReasonViewSet.as_view(
        {'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}),
         name='leavereason-detail'),

    path('student-group-leaves/', StudentGroupLeavesViewSet.as_view({'get': 'list', 'post': 'create'}),
         name='studentgroupleaves-list'),
    path('student-group-leaves/<uuid:pk>/', StudentGroupLeavesViewSet.as_view(
        {'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}),
         name='studentgroupleaves-detail'),

    path('student-freezes/', StudentFreezesViewSet.as_view({'get': 'list', 'post': 'create'}),
         name='studentfreezes-list'),
    path('student-freezes/<uuid:pk>/', StudentFreezesViewSet.as_view(
        {'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}),
         name='studentfreezes-detail'),

    path('student-balance-history/', StudentBalanceHistoryViewSet.as_view({'get': 'list', 'post': 'create'}),
         name='studentbalancehistory-list'),
    path('student-balance-history/<uuid:pk>/', StudentBalanceHistoryViewSet.as_view(
        {'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}),
         name='studentbalancehistory-detail'),

    path('attendences/', AttendenceViewSet.as_view({'get': 'list', 'post': 'create'}), name='attendence-list'),
    path('attendences/<uuid:pk>/', AttendenceViewSet.as_view(
        {'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}),
         name='attendence-detail'),

    # ==================== GROUP URLs ====================
    path('rooms/', RoomViewSet.as_view({'get': 'list', 'post': 'create'}), name='room-list'),
    path('rooms/<uuid:pk>/',
         RoomViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}),
         name='room-detail'),

    path('courses/', CourseViewSet.as_view({'get': 'list', 'post': 'create'}), name='course-list'),
    path('courses/<uuid:pk>/',
         CourseViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}),
         name='course-detail'),



    path('group-teachers/', GroupTeacherViewSet.as_view({'get': 'list', 'post': 'create'}), name='groupteacher-list'),
    path('group-teachers/<uuid:pk>/', GroupTeacherViewSet.as_view(
        {'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}),
         name='groupteacher-detail'),

    # ==================== GROUP URLS ====================

    path('groups/', GroupListCreateView.as_view(), name='group-list-create'),


    path('groups/<uuid:pk>/', GroupDetailUpdateDeleteView.as_view(), name='group-detail'),

    # ==================== GROUP TEACHER URLS ====================

    # Guruh o'qituvchilari ro'yxati va qo'shish
    # GET: /api/groups/<group_id>/teachers/ - Guruh o'qituvchilarini olish
    # POST: /api/groups/<group_id>/teachers/ - Guruhga o'qituvchi qo'shish
    path('groups/<uuid:group_pk>/teachers/', views.group_teacher_list_create, name='group-teacher-list'),

    # Guruh o'qituvchisi: detail, update, delete
    # GET: /api/groups/<group_id>/teachers/<id>/ - O'qituvchi ma'lumotlari
    # PUT: /api/groups/<group_id>/teachers/<id>/ - O'qituvchi ma'lumotini to'liq yangilash
    # PATCH: /api/groups/<group_id>/teachers/<id>/ - O'qituvchi ma'lumotini qisman yangilash
    # DELETE: /api/groups/<group_id>/teachers/<id>/ - O'qituvchini guruhdan o'chirish
    path('groups/<uuid:group_pk>/teachers/<uuid:pk>/', views.group_teacher_detail_update_delete,
         name='group-teacher-detail'),

    # ==================== HELPER URLS ====================

    # Kurslar ro'yxati (dropdown uchun)
    # GET: /api/courses/ - Barcha kurslarni olish
    path('courses/', views.course_list, name='course-list'),

    # Xonalar ro'yxati (dropdown uchun)
    # GET: /api/rooms/ - Barcha xonalarni olish
    path('rooms/', views.room_list, name='room-list'),

    # Bo'sh xonalarni olish
    # GET: /api/rooms/available/?lesson=<id>&start_date=<date>&end_date=<date>
    path('rooms/available/', views.available_rooms, name='available-rooms'),

    # Guruhlar statistikasi
    # GET: /api/groups/statistics/ - Guruhlar statistikasi
    path('statistics/', views.group_statistics, name='group-statistics'),

    # ==================== LESSON URLs ====================
    path('lesson-times/', LessonTimeViewSet.as_view({'get': 'list', 'post': 'create'}), name='lessontime-list'),
    path('lesson-times/<uuid:pk>/', LessonTimeViewSet.as_view(
        {'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}),
         name='lessontime-detail'),

    path('lesson-schedules/', LessonScheduleViewSet.as_view({'get': 'list', 'post': 'create'}),
         name='lessonschedule-list'),
    path('lesson-schedules/<uuid:pk>/', LessonScheduleViewSet.as_view(
        {'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}),
         name='lessonschedule-detail'),

    path('exams/', ExamsViewSet.as_view({'get': 'list', 'post': 'create'}), name='exams-list'),
    path('exams/<uuid:pk>/',
         ExamsViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}),
         name='exams-detail'),

    path('exam-results/', ExamResultsViewSet.as_view({'get': 'list', 'post': 'create'}), name='examresults-list'),
    path('exam-results/<uuid:pk>/', ExamResultsViewSet.as_view(
        {'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}),
         name='examresults-detail'),


    # ==================== TEACHER URLs ====================
    path('teacher-salary-rules/', TeacherSalaryRulesViewSet.as_view({'get': 'list', 'post': 'create'}),
         name='teachersalaryrules-list'),
    path('teacher-salary-rules/<uuid:pk>/', TeacherSalaryRulesViewSet.as_view(
        {'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}),
         name='teachersalaryrules-detail'),

    path('teacher-salary-payments/', TeacherSalaryPaymentsViewSet.as_view({'get': 'list', 'post': 'create'}),
         name='teachersalarypayments-list'),
    path('teacher-salary-payments/<uuid:pk>/', TeacherSalaryPaymentsViewSet.as_view(
        {'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}),
         name='teachersalarypayments-detail'),

    path('teacher-salary-calculations/', TeacherSalaryCalculationsViewSet.as_view({'get': 'list', 'post': 'create'}),
         name='teachersalarycalculations-list'),
    path('teacher-salary-calculations/<uuid:pk>/', TeacherSalaryCalculationsViewSet.as_view(
        {'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}),
         name='teachersalarycalculations-detail')    ,


    # 1. Guruh to'liq ma'lumotlari
    path('groups/<uuid:pk>/info/', views.group_full_info, name='group-info'),

    # 2. Davomat
    path('groups/<uuid:group_pk>/attendance/', views.attendance_list_create, name='attendance'),

    # 3. O'quvchilar ro'yxati
    path('groups/<uuid:group_pk>/students/', views.students_list, name='students-list'),

    # 5. Guruh operatsiyalari
    path('groups/<uuid:group_pk>/add-student/', views.add_student, name='add-student'),
    path('groups/<uuid:group_pk>/students/<uuid:student_group_pk>/', views.remove_student, name='remove-student'),
    path('groups/<uuid:group_pk>/send-sms/', views.send_sms, name='send-sms'),

    # 6. Chegirmalar
    path('discounts/', views.discount_list_create, name='discounts'),
    path('discounts/<uuid:pk>/', views.discount_detail, name='discount-detail'),

    # 7. Imtihonlar
    path('exams/', views.exam_list_create, name='exams'),
    path('exams/<uuid:pk>/', views.exam_detail, name='exam-detail'),
    path('exams/<uuid:exam_pk>/results/', views.exam_results, name='exam-results'),

    # 8. Tarix
    path('groups/<uuid:group_pk>/history/', views.group_history, name='group-history'),

    # ==================== YANGI: O'QUVCHI QIDIRISH VA FAOLLASHTIRISH ====================

    # 1. O'quvchini qidirish
    # GET /api/students/search/?q=ismi_yoki_raqami
    path('students/search/', views.student_search, name='student-search'),

    # 2. Guruhga talaba qo'shish (yangilangan)
    # POST /api/groups/<group_id>/add-student/
    # Bu URL allaqachon bor, faqat viewni almashtiring
    # path('groups/<uuid:group_pk>/add-student/', views.add_student_to_group, name='add-student-to-group'),

    # 3. Talabani faollashtirish (balansga pul qo'shish)
    # PUT /api/students/<student_id>/activate/
    path('students/<uuid:student_pk>/activate/', views.activate_student, name='activate-student'),

    # 4. Talaba balansi va holati
    # GET /api/students/<student_id>/balance-status/
    path('students/<uuid:student_pk>/balance-status/', views.student_balance_status, name='student-balance-status'),

# ============ ONLAYN DARSLAR URLs ============

# Mavjud urls.py ga QO'SHING:


    # ... mavjud URLlar

    # ONLAYN DARSLAR
    path('groups/<uuid:group_pk>/online-lessons/', views.group_online_lessons, name='group-online-lessons'),
    path('online-lessons/<uuid:pk>/', views.online_lesson_detail, name='online-lesson-detail'),
    path('online-lessons/<uuid:pk>/publish/', views.publish_lesson, name='publish-lesson'),
    path('online-lessons/<uuid:pk>/unpublish/', views.unpublish_lesson, name='unpublish-lesson'),
    # Chegirma yaratish
    path('groups/<uuid:group_pk>/students/<uuid:student_group_pk>/discount/',
         views.create_student_discount,
         name='create-student-discount'),

    # Chegirma ko'rish
    path('groups/<uuid:group_pk>/students/<uuid:student_group_pk>/discount/',
         views.get_student_discount,
         name='get-student-discount'),

    # Chegirma yangilash
    path('groups/<uuid:group_pk>/students/<uuid:student_group_pk>/discount/',
         views.update_student_discount,
         name='update-student-discount'),

    # Chegirma bekor qilish
    path('groups/<uuid:group_pk>/students/<uuid:student_group_pk>/discount/',
         views.delete_student_discount,
         name='delete-student-discount'),

    # To'lov farqini hisoblash
    path('groups/<uuid:group_pk>/students/<uuid:student_group_pk>/discount/calculate/',
         views.calculate_payment_difference,
         name='calculate-payment-difference'),
    # DARS SANASI BOSHQARUVI

    # Guruh darslarini olish
    path('groups/<uuid:group_pk>/lessons/',
         views.group_lessons,
         name='group-lessons'),

    # Tanlangan darsni aniqlash
    path('groups/<uuid:group_pk>/lessons/<uuid:lesson_pk>/',
         views.lesson_detail,
         name='lesson-detail'),

    # Dars sanasini ko'chirish
    path('groups/<uuid:group_pk>/lessons/<uuid:lesson_pk>/move-date/',
         views.move_lesson_date,
         name='move-lesson-date'),

    # Yangi sana band emasligini tekshirish
    path('groups/<uuid:group_pk>/lessons/check-availability/',
         views.check_time_availability,
         name='check-time-availability'),
    # TARK ETGAN TALABALAR HISOBOTI

    # Asosiy hisobot
    path('reports/student-leaves/',
         views.student_leave_report,
         name='student-leave-report'),

    # Filter uchun ma'lumotlar
    path('reports/leave-reasons/',
         views.leave_reasons_list,
         name='leave-reasons-list'),

    path('reports/teachers/',
         views.teachers_list,
         name='teachers-list'),

    path('reports/courses/',
         views.courses_list,
         name='courses-list'),
    # Darsni bekor qilish
    path('groups/<uuid:group_pk>/lessons/<uuid:lesson_pk>/cancel/',
         views.cancel_lesson,
         name='cancel-lesson'),

    # Bekor qilingan darslar ro'yxati
    path('groups/<uuid:group_pk>/cancelled-lessons/',
         views.cancelled_lessons_list,
         name='cancelled-lessons-list'),

    # Darsni qayta tiklash
    path('cancelled-lessons/<uuid:audit_pk>/restore/',
         views.restore_lesson,
         name='restore-lesson'),
    # Chegirma belgilash
    path('groups/<uuid:group_pk>/students/<uuid:student_group_pk>/discount-price/',
         views.set_discount_price,
         name='set-discount-price'),

    # Chegirmani ko'rish
    path('groups/<uuid:group_pk>/students/<uuid:student_group_pk>/discount-price/',
         views.get_student_discount,
         name='get-student-discount'),

    # Chegirmani bekor qilish
    path('groups/<uuid:group_pk>/students/<uuid:student_group_pk>/discount-price/',
         views.cancel_discount,
         name='cancel-discount'),

    # Chegirmalar tarixi
    path('groups/<uuid:group_pk>/students/<uuid:student_group_pk>/discount-price/history/',
         views.discount_history,
         name='discount-history'),
    # Guruh to'liq tarixi - barcha harakatlar bitta endpointda
    path('groups/<uuid:group_id>/history/', GroupHistoryView.as_view(), name='group-history'),

    # Alohida tarix turlari
    path('groups/<uuid:group_id>/history/teachers/', GroupTeacherHistoryView.as_view(), name='group-teachers-history'),
    path('groups/<uuid:group_id>/history/students/', GroupStudentsHistoryView.as_view(), name='group-students-history'),
    path('groups/<uuid:group_id>/history/freezes/', GroupFreezesHistoryView.as_view(), name='group-freezes-history'),
    path('groups/<uuid:group_id>/history/audit/', GroupAuditLogView.as_view(), name='group-audit-log'),
    # Talabani o'tkazish
    path('students/transfer/', StudentTransferView.as_view(), name='student-transfer'),

    # Muzlatish
    path('students/freeze/', StudentFreezeView.as_view(), name='student-freeze'),
    path('students/<uuid:student_id>/freezes/', StudentFreezesListView.as_view(), name='student-freezes-list'),

    # Guruhdan chiqarish
    path('students/leave/', StudentLeaveView.as_view(), name='student-leave'),

    # Talaba guruhlari
    path('students/<uuid:student_id>/groups/', StudentActiveGroupsView.as_view(), name='student-active-groups'),

    # Balansni qayta hisoblash
    path('students/balance/recalculate/', BalanceRecalculationView.as_view(), name='balance-recalculate'),






    # Arxivlash
    path('groups/<uuid:group_id>/archive/', GroupArchiveView.as_view(), name='group-archive'),
    path('groups/<uuid:group_id>/unarchive/', GroupUnarchiveView.as_view(), name='group-unarchive'),

    # Excel export
    path('groups/export/excel/', GroupExportExcelView.as_view(), name='groups-export-excel'),

    # Statistika
    path('groups/statistics/', GroupStatisticsView.as_view(), name='groups-statistics'),

    # Bulk actions
    path('groups/bulk-action/', GroupBulkActionView.as_view(), name='groups-bulk-action'),

    # Guruhlarni export qilish
    path('export/groups/', GroupsExportView.as_view(), name='export-groups'),

    # Talabalarni export qilish
    path('export/students/', StudentsExportView.as_view(), name='export-students'),

    # Export tarixi
    path('export/history/', ExportHistoryView.as_view(), name='export-history'),

    # Export statistikasi
    path('export/statistics/', ExportStatisticsView.as_view(), name='export-statistics'),
    # Imtihonlar ro'yxati
    path('exams/', ExamsListView.as_view(), name='exams-list'),

    # Imtihon yaratish
    path('exams/create/', ExamCreateView.as_view(), name='exam-create'),

    # Imtihon batafsil, tahrirlash, o'chirish
    path('exams/<uuid:exam_id>/', ExamDetailView.as_view(), name='exam-detail'),

    # Baholash (single yoki bulk)
    path('exams/grade/', ExamGradingView.as_view(), name='exam-grading'),

    # Imtihon natijalari
    path('exams/<uuid:exam_id>/results/', ExamResultsView.as_view(), name='exam-results'),

    # Imtihon statistikasi
    path('exams/<uuid:exam_id>/statistics/', ExamStatisticsView.as_view(), name='exam-statistics'),

    # Qatnashuvchilar sozlamalari (CEO uchun)
    path('exams/settings/participants/', ExamParticipantsSettingsView.as_view(), name='exam-participants-settings'),
    # Onlayn darslar ro'yxati
    path('online-lessons/', OnlineLessonsListView.as_view(), name='online-lessons-list'),

    # Mavzu belgilash (bitta dars)
    path('lessons/set-topic/', SetLessonTopicView.as_view(), name='set-lesson-topic'),

    # Mavzu o'zgartirish
    path('lessons/update-topic/', UpdateLessonTopicView.as_view(), name='update-lesson-topic'),

    # Guruh dars kalendari
    path('lessons/calendar/', GroupLessonsCalendarView.as_view(), name='group-lessons-calendar'),

    # Ko'p darsga mavzu belgilash (yillik/oylik reja)
    path('lessons/bulk-set-topics/', BulkSetLessonTopicsView.as_view(), name='bulk-set-lesson-topics'),

    # Darsni nashr qilish/yashirish
    path('online-lessons/<uuid:lesson_id>/publish/', PublishLessonView.as_view(), name='publish-lesson'),

    # Darslar statistikasi
    path('lessons/<uuid:group_id>/statistics/', LessonStatisticsView.as_view(), name='lesson-statistics'),
    path("online-lessons/", OnlineLessonCreateView.as_view(), name="online-lesson-list"),
    path("online-lessons/<uuid:pk>/", OnlineLessonDetailView.as_view(), name="online-lesson-detail"),

    # ── RO'YXAT + YARATISH
    path('students/create/list/', views.student_list_create, name='student-list-create'),

    # ── FILTER OPTIONS
    path('students/filter-options/', views.student_filter_options, name='student-filter-options'),

    # ── EXPORT (filter params ishlaydi)
    path('students/export/', views.student_export_excel, name='student-export'),

    # ── DETAIL / TAHRIRLASH / O'CHIRISH
    path('students/<uuid:pk>/crud/', views.student_detail_update_delete, name='student-detail'),

    # ── TABLAR
    path('students/<uuid:pk>/groups/',       views.student_groups_tab,       name='student-groups-tab'),
    path('students/<uuid:pk>/transactions/', views.student_transactions_tab, name='student-transactions-tab'),
    path('students/<uuid:pk>/sms/',          views.student_sms_tab,          name='student-sms-tab'),
    path('students/<uuid:pk>/calls/',        views.student_calls_tab,        name='student-calls-tab'),
    path('students/<uuid:pk>/history/',      views.student_history_tab,      name='student-history-tab'),
    path('students/<uuid:pk>/lead-history/', views.student_lead_history_tab, name='student-lead-tab'),
    path('students/<uuid:pk>/coin-history/', views.student_coin_history_tab, name='student-coin-tab'),

    # ── AMALLAR
    path('students/<uuid:pk>/payment/',           views.student_add_payment,       name='student-payment'),
    path('students/<uuid:pk>/add-to-group/',      views.student_add_to_group,      name='student-add-group'),
    path('students/<uuid:pk>/remove-from-group/', views.student_remove_from_group, name='student-remove-group'),
    path('students/<uuid:pk>/freeze/',            views.student_freeze,            name='student-freeze'),
    path('students/<uuid:pk>/unfreeze/',          views.student_unfreeze,          name='student-unfreeze'),
    path('students/<uuid:pk>/send-sms/',          views.student_send_sms,          name='student-send-sms'),



#     MethodURLTavsifGET/POST/students/Ro'yxat + filterlar, yangi yaratishGET/students/filter-options/Dropdownlar uchunGET/PUT/PATCH/DELETE/students/{id}/Detail, tahrirlash, o'chirishGET/students/{id}/groups/Guruhlar tabGET/students/{id}/transactions/To'lovlar tabGET/students/{id}/sms/SMS tabGET/students/{id}/calls/Qo'ng'iroq tarixi tabGET/students/{id}/history/Tarix tabGET/students/{id}/lead-history/Lid tarixi tabGET/students/{id}/coin-history/Coin tarix tabPOST/students/{id}/payment/To'lov qilishPOST/students/{id}/add-to-group/Guruhga qo'shish
#     MethodURLNima qiladiPOST/students/{id}/remove-from-group/Guruhdan chiqarish, StudentGroupLeaves yozuvi ham yaratadiPOST/students/{id}/freeze/Muzlatish (freeze_start_date, freeze_end_date, reason)POST/students/{id}/unfreeze/Muzlatishni bekor qilishPOST/students/{id}/send-sms/SMS yuborish (text, template_id)GET/students/export/Excel export (filterlar ishlaydi)
#     pip install openpyxl

# academics/urls.py ga qo'shish uchun tayyor kod



    # 1. Guruhlar ro'yxati + filterlar (birinchi rasm — asosiy sahifa)
    path('v1/groups/', views.GroupListView.as_view(), name='group-list'),

    # 2. Yangi guruh qo'shish (Yangi guruh oynasi)
    path('v1/groups/create/', views.GroupCreateView.as_view(), name='group-create'),

    # 3. Bitta guruh kartasi / to'liq ma'lumot
    path('v1/groups/<uuid:pk>/', views.GroupDetailView.as_view(), name='group-detail'),

    # 4. Guruhdagi talabalar ro'yxati + filter (talabalar bo'limi)
    path('v1/groups/<uuid:group_id>/students/', views.GroupStudentsView.as_view(), name='group-students'),

    # 5. Talaba qidirish (guruhga talaba qo'shish oynasida eng muhim)
    path('v1/students/search/', views.StudentSearchView.as_view(), name='student-search'),
    # 7. Talabaga to'lov qo'shish (To'lov oynasi)
    path('students/<uuid:student_id>/add-payment/', views.StudentAddPaymentView.as_view(), name='add-payment'),

    # 6. Talaba kartasi (o'ng tarafdagi panel)
    path('v1/students/<uuid:pk>/detail/', views.StudentDetailView.as_view(), name='student-detail'),



    # 8. Guruh davomati (davomat sahifasi)
    path('v1/groups/<uuid:group_id>/attendance/', views.GroupAttendanceView.as_view(), name='groupbirbalo'),

    # 9. Davomatni saqlash (bir kunga)
    path('v1/groups/<uuid:group_id>/attendance/save/', views.AttendanceSaveView.as_view(), name='save-attendance'),

    # 10. Guruh chegirmalari / talabaga chegirma qo'yish
    path('v1/groups/<uuid:group_id>/discounts/', views.GroupDiscountsView.as_view(), name='group-discounts'),

    # 11. Bitta talabaga chegirma berish / narxni o'zgartirish
    path('v1/groups/<uuid:group_id>/students/<uuid:sg_id>/set-discount/',
         views.SetStudentDiscountView.as_view(), name='set-student-discount'),

    # 12. Imtihonlar ro'yxati (imtihon bo'limi)
    path('v1/exams/', views.ExamListView.as_view(), name='exam-list'),

    # 13. Yangi imtihon qo'shish
    path('v1/exams/create/', views.ExamCreateView.as_view(), name='exam-create'),

    # 14. Imtihon natijalarini kiritish
    path('v1/exams/<uuid:exam_id>/results/', views.ExamResultsSubmitView.as_view(), name='exam-results'),

    # 15. Onlayn darslar / mavzular (onlayn materiallar bo'limi)
    path('v1/groups/<uuid:group_id>/online-lessons/', views.GroupOnlineLessonsView.as_view(), name='group-online-lessons'),
# academics/urls.py ga qo'shing (oldingi pathlar ostiga)


    # 16. Guruhni tahrirlash (Guruhni tahrirlash oynasi — Saqlash / Bekor qilish)
    # PATCH /v1/groups/<uuid:group_id>/
    # Body misoli: {"name": "NewFrontEnd", "course": uuid, "teacher": uuid, "start_date": "..."}
    # PUT bilan ham ishlatish mumkin, lekin PATCH qisman o'zgartirish uchun yaxshi



    path('v1/groups/<uuid:group_id>/update/', views.GroupUpdateView.as_view(), name='group-update'),

    # 17. Guruhga SMS yuborish (Guruhga SMS yuborish oynasi)
    # POST /v1/groups/<uuid:group_id>/send-sms/
    # Body: {"message": "Salom talabalar!", "send_to": "students" yoki "parents" yoki "all"}



    path('v1/groups/<uuid:group_id>/send-sms/', views.GroupSendSMSView.as_view(), name='group-send-sms'),

    # 18. Yangi talaba yaratish + guruhga qo'shish (Yangi talaba oynasi)
    # POST /v1/groups/<uuid:group_id>/add-new-student/
    # Body: {"full_name": "Ali Valiev", "phone_number": "+998901234567", "joined_at": "2026-03-12"}
    # (Sanani kiritish majburiy, telefon/ism bo'yicha validatsiya)



    path('v1/groups/<uuid:group_id>/add-new-student/', views.GroupAddNewStudentView.as_view(), name='group-add-new-student'),

    # 19. Talabalar ro'yxatini saralash (A-Z / Z-A bo'yicha) — bu allaqachon bor endpointda qo'llaniladi
    # GET /v1/groups/<uuid:group_id>/students/?ordering=full_name yoki ?ordering=-full_name
    # (Bu qo'shimcha emas, faqat GroupStudentsView ga ordering qo‘shiladi)


]

