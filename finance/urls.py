from django.urls import path
from .views import ExpenseCategoryViewSet, ExpensesViewSet, MonthlyIncomeViewSet, PaymentViewSet, SaleViewSet, \
    ExpenseSubcategoryViewSet, DetailedExpenseViewSet, BonusViewSet, FineViewSet, SalaryViewSet, CallLogViewSet, \
    AllPaymentsAPIView, WithdrawalsAPIView, ExpensesAPIView, ExpenseDetailAPIView, ExpenseCategoryAPIView, \
    ExpenseCategoryDetailAPIView, TeacherSalaryRulesAPIView, TeacherSalaryRuleDetailAPIView, \
    TeacherSalaryCalculateAPIView, DebtorsAPIView
from .views import TeacherSalaryRulesViewSet, TeacherSalaryPaymentsViewSet, TeacherSalaryCalculationsViewSet,StudentDebtsViewSet, TeacherDebtsViewSet, AllDebtsView,ConversionReportViewSet, CRMLeadViewSet,LeadsReportViewSet,StudentLeavesReportViewSet, StudentGroupLeavesViewSet, LeaveReasonViewSet,WorklyIntegrationViewSet, WorklyAttendanceViewSet

urlpatterns = [
    # bu barcha tolovlar uchun api  paymentgaca
    # ExpenseCategory URLs
    path('expense-categories/', ExpenseCategoryViewSet.as_view({'get': 'list', 'post': 'create'}),
         name='expensecategory-list'),
    path('expense-categories/<uuid:pk>/', ExpenseCategoryViewSet.as_view(
        {'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}),
         name='expensecategory-detail'),

    # Expenses URLs
    path('expenses/', ExpensesViewSet.as_view({'get': 'list', 'post': 'create'}), name='expenses-list'),
    path('expenses/<uuid:pk>/',
         ExpensesViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}),
         name='expenses-detail'),


    path('expenses/monthly-summary/', ExpensesViewSet.as_view({'get': 'monthly_summary'}),
         name='expenses-monthly-summary'),

    # MonthlyIncome
    path('monthly-income/', MonthlyIncomeViewSet.as_view({'get': 'list', 'post': 'create'}),
         name='monthly-income-list'),
    path('monthly-income/<uuid:pk>/', MonthlyIncomeViewSet.as_view(
        {'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}),
         name='monthly-income-detail'),
    path('monthly-income/<uuid:pk>/net-profit/', MonthlyIncomeViewSet.as_view({'get': 'net_profit'}),
         name='monthly-income-net-profit'),

    # Payment
    path('payments/', PaymentViewSet.as_view({'get': 'list', 'post': 'create'}), name='payment-list'),
    path('payments/<uuid:pk>/',
         PaymentViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}),
         name='payment-detail'),
# Sales   yechib olishlar u-n
path('sales/', SaleViewSet.as_view({'get': 'list', 'post': 'create'}), name='sale-list'),
path('sales/<uuid:pk>/', SaleViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='sale-detail'),
path('sales/statistics/', SaleViewSet.as_view({'get': 'statistics'}), name='sale-statistics'),
path('sales/active-count/', SaleViewSet.as_view({'get': 'active_count'}), name='sale-active-count'),
# xarajatlar
# ExpenseSubcategory
path('expense-subcategories/', ExpenseSubcategoryViewSet.as_view({'get': 'list', 'post': 'create'}), name='subcategory-list'),
path('expense-subcategories/<uuid:pk>/', ExpenseSubcategoryViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='subcategory-detail'),

# DetailedExpense
path('detailed-expenses/', DetailedExpenseViewSet.as_view({'get': 'list', 'post': 'create'}), name='detailed-expense-list'),
path('detailed-expenses/<uuid:pk>/', DetailedExpenseViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='detailed-expense-detail'),
path('detailed-expenses/chart-data/', DetailedExpenseViewSet.as_view({'get': 'chart_data'}), name='detailed-expense-charts'),
path('detailed-expenses/directors-summary/', DetailedExpenseViewSet.as_view({'get': 'directors_summary'}), name='directors-summary'),
# Bonus
path('bonuses/', BonusViewSet.as_view({'get': 'list', 'post': 'create'}), name='bonus-list'),
path('bonuses/<uuid:pk>/', BonusViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='bonus-detail'),

# Fine
path('fines/', FineViewSet.as_view({'get': 'list', 'post': 'create'}), name='fine-list'),
path('fines/<uuid:pk>/', FineViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='fine-detail'),

# Salary
path('salaries/', SalaryViewSet.as_view({'get': 'list', 'post': 'create'}), name='salary-list'),
path('salaries/<uuid:pk>/', SalaryViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='salary-detail'),
path('salaries/calculate/', SalaryViewSet.as_view({'post': 'calculate'}), name='salary-calculate'),
path('salaries/summary/', SalaryViewSet.as_view({'get': 'summary'}), name='salary-summary'),


path('teacher-salary-rules/', TeacherSalaryRulesViewSet.as_view({'get': 'list', 'post': 'create'}), name='teacher-salary-rules-list'),
path('teacher-salary-rules/<uuid:pk>/', TeacherSalaryRulesViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='teacher-salary-rules-detail'),
path('teacher-salary-rules/bulk-create/', TeacherSalaryRulesViewSet.as_view({'post': 'bulk_create'}), name='teacher-salary-rules-bulk'),


path('teacher-salary-payments/', TeacherSalaryPaymentsViewSet.as_view({'get': 'list', 'post': 'create'}), name='teacher-salary-payments-list'),
path('teacher-salary-payments/<uuid:pk>/', TeacherSalaryPaymentsViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='teacher-salary-payments-detail'),
path('teacher-salary-payments/summary/', TeacherSalaryPaymentsViewSet.as_view({'get': 'summary'}), name='teacher-salary-payments-summary'),


path('teacher-salary-calculations/', TeacherSalaryCalculationsViewSet.as_view({'get': 'list', 'post': 'create'}), name='teacher-salary-calculations-list'),
path('teacher-salary-calculations/<uuid:pk>/', TeacherSalaryCalculationsViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='teacher-salary-calculations-detail'),
path('teacher-salary-calculations/calculate/', TeacherSalaryCalculationsViewSet.as_view({'post': 'calculate'}), name='teacher-salary-calculations-calculate'),
path('teacher-salary-calculations/monthly-report/', TeacherSalaryCalculationsViewSet.as_view({'get': 'monthly_report'}), name='teacher-salary-calculations-report'),





path('teacher-salary-rules/get-by-period/', TeacherSalaryRulesViewSet.as_view({'post': 'get_by_period'}), name='salary-rules-by-period'),
path('teacher-salary-rules/configure-period/', TeacherSalaryRulesViewSet.as_view({'post': 'configure_period'}), name='salary-configure-period'),
path('teacher-salary-rules/active-periods/', TeacherSalaryRulesViewSet.as_view({'get': 'active_periods'}), name='salary-active-periods'),
path('teacher-salary-rules/period-summary/', TeacherSalaryRulesViewSet.as_view({'get': 'period_summary'}), name='salary-period-summary'),


# qarzdorlar
# Student Debts
path('student-debts/', StudentDebtsViewSet.as_view({'get': 'list'}), name='student-debts-list'),
path('student-debts/<uuid:pk>/', StudentDebtsViewSet.as_view({'get': 'retrieve'}), name='student-debts-detail'),
path('student-debts/summary/', StudentDebtsViewSet.as_view({'get': 'summary'}), name='student-debts-summary'),

# Teacher Debts
path('teacher-debts/', TeacherDebtsViewSet.as_view({'get': 'list'}), name='teacher-debts-list'),
path('teacher-debts/summary/', TeacherDebtsViewSet.as_view({'get': 'summary'}), name='teacher-debts-summary'),

# All Debts
path('all-debts/', AllDebtsView.as_view(), name='all-debts'),
# konversiya

# Conversion Reports
path('conversion-reports/overview/', ConversionReportViewSet.as_view({'get': 'overview'}), name='conversion-overview'),
path('conversion-reports/funnel/', ConversionReportViewSet.as_view({'get': 'funnel'}), name='conversion-funnel'),
path('conversion-reports/by-source/', ConversionReportViewSet.as_view({'get': 'by_source'}), name='conversion-by-source'),
path('conversion-reports/by-employee/', ConversionReportViewSet.as_view({'get': 'by_employee'}), name='conversion-by-employee'),
path('conversion-reports/pipeline-transitions/', ConversionReportViewSet.as_view({'get': 'pipeline_transitions'}), name='pipeline-transitions'),
path('conversion-reports/lost-reasons/', ConversionReportViewSet.as_view({'get': 'lost_reasons'}), name='lost-reasons'),

# CRM Leads
path('crm-leads/', CRMLeadViewSet.as_view({'get': 'list', 'post': 'create'}), name='crm-leads-list'),
path('crm-leads/<uuid:pk>/', CRMLeadViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='crm-leads-detail'),



# Lidlar hisoboti
path('leads-report/statistics/', LeadsReportViewSet.as_view({'get': 'statistics'}), name='leads-report-statistics'),
path('leads-report/pie-chart/', LeadsReportViewSet.as_view({'get': 'pie_chart'}), name='leads-report-pie'),
path('leads-report/bar-chart/', LeadsReportViewSet.as_view({'get': 'bar_chart'}), name='leads-report-bar'),
path('leads-report/summary/', LeadsReportViewSet.as_view({'get': 'summary'}), name='leads-report-summary'),
path('leads-report/detailed-report/', LeadsReportViewSet.as_view({'get': 'detailed_report'}), name='leads-report-detailed'),



# Guruhni tark etgan o'quvchilar hisoboti
path('student-leaves-report/statistics/', StudentLeavesReportViewSet.as_view({'get': 'statistics'}), name='leaves-report-statistics'),
path('student-leaves-report/by-teacher/', StudentLeavesReportViewSet.as_view({'get': 'by_teacher'}), name='leaves-by-teacher'),
path('student-leaves-report/by-course/', StudentLeavesReportViewSet.as_view({'get': 'by_course'}), name='leaves-by-course'),
path('student-leaves-report/by-month/', StudentLeavesReportViewSet.as_view({'get': 'by_month'}), name='leaves-by-month'),
path('student-leaves-report/by-reason/', StudentLeavesReportViewSet.as_view({'get': 'by_reason'}), name='leaves-by-reason'),
path('student-leaves-report/detailed-list/', StudentLeavesReportViewSet.as_view({'get': 'detailed_list'}), name='leaves-detailed-list'),

# StudentGroupLeaves CRUD
path('student-group-leaves/', StudentGroupLeavesViewSet.as_view({'get': 'list', 'post': 'create'}), name='student-leaves-list'),
path('student-group-leaves/<uuid:pk>/', StudentGroupLeavesViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='student-leaves-detail'),

# LeaveReason
path('leave-reasons/', LeaveReasonViewSet.as_view({'get': 'list', 'post': 'create'}), name='leave-reason-list'),
path('leave-reasons/<uuid:pk>/', LeaveReasonViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='leave-reason-detail'),



# Workly Integration
path('workly-integration/', WorklyIntegrationViewSet.as_view({'get': 'list', 'post': 'create'}), name='workly-integration-list'),
path('workly-integration/<uuid:pk>/', WorklyIntegrationViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='workly-integration-detail'),
path('workly-integration/test-connection/', WorklyIntegrationViewSet.as_view({'post': 'test_connection'}), name='workly-test-connection'),
path('workly-integration/<uuid:pk>/activate/', WorklyIntegrationViewSet.as_view({'post': 'activate'}), name='workly-activate'),
path('workly-integration/<uuid:pk>/deactivate/', WorklyIntegrationViewSet.as_view({'post': 'deactivate'}), name='workly-deactivate'),
path('workly-integration/<uuid:pk>/sync-attendance/', WorklyIntegrationViewSet.as_view({'post': 'sync_attendance'}), name='workly-sync'),
path('workly-integration/status/', WorklyIntegrationViewSet.as_view({'get': 'status'}), name='workly-status'),

# Workly Attendance
path('workly-attendance/', WorklyAttendanceViewSet.as_view({'get': 'list'}), name='workly-attendance-list'),
path('workly-attendance/<uuid:pk>/', WorklyAttendanceViewSet.as_view({'get': 'retrieve'}), name='workly-attendance-detail'),
path('workly-attendance/summary/', WorklyAttendanceViewSet.as_view({'get': 'summary'}), name='workly-attendance-summary'),
# Qo'ng'iroqlar jurnali
path('call-logs/', CallLogViewSet.as_view({'get': 'list', 'post': 'create'}), name='call-log-list'),
path('call-logs/<uuid:pk>/', CallLogViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='call-log-detail'),
path('call-logs/statistics/', CallLogViewSet.as_view({'get': 'statistics'}), name='call-log-statistics'),
path('call-logs/daily-report/', CallLogViewSet.as_view({'get': 'daily_report'}), name='call-log-daily'),
path('call-logs/operator-performance/', CallLogViewSet.as_view({'get': 'operator_performance'}), name='call-log-operators'),
path('call-logs/<uuid:pk>/audio/', CallLogViewSet.as_view({'get': 'audio'}), name='call-log-audio'),





path('v1/finance/payments/', AllPaymentsAPIView.as_view(), name='all-payments'),


# finance/urls.py
path('v1/finance/withdrawals/', WithdrawalsAPIView.as_view(), name='finance-withdrawals'),


# xarajatlar
    # Xarajatlar (jadval + yangi qo'shish + filter + grafik)
    path('v1/finance/expenses/', ExpensesAPIView.as_view(), name='expenses-list-create'),
    path('v1/finance/expenses/<uuid:pk>/', ExpenseDetailAPIView.as_view(), name='expense-detail'),

    # Kategoriyalar (dropdown + qo'shish + tahrirlash + o'chirish)
    path('v1/finance/expense-categories/', ExpenseCategoryAPIView.as_view(), name='expense-categories'),
    path('v1/finance/expense-categories/<uuid:pk>/', ExpenseCategoryDetailAPIView.as_view(), name='expense-category-detail'),




# #,Funksiya (rasmdagi joy),Method,Endpoint,Izoh / Nima qiladi?
# 1,Xarajatlar ro‘yxati + filterlar + jami summa,GET,/v1/finance/expenses/,Jadval + grafik + jami summa
# 2,Yangi xarajat qo‘shish,POST,/v1/finance/expenses/,Formadan ma'lumot saqlash
# 3,Xarajatni tahrirlash,PATCH,/v1/finance/expenses/<id>/,Bitta xarajatni o‘zgartirish
# 4,Xarajatni o‘chirish,DELETE,/v1/finance/expenses/<id>/,O‘chirish tugmasi
# 5,Xarajat kategoriyalari ro‘yxati,GET,/v1/finance/expense-categories/,Dropdown uchun
# 6,Yangi kategoriya qo‘shish,POST,/v1/finance/expense-categories/,Kategoriya qo‘shish oynasi
# 7,Kategoriyani tahrirlash,PATCH,/v1/finance/expense-categories/<id>/,Tahrirlash tugmasi
# 8,Kategoriyani o‘chirish,DELETE,/v1/finance/expense-categories/<id>/,O‘chirish tugmasi
# finance/urls.py


    # Ish haqi qoidalari (standart + individual)
    path('v1/finance/teacher-salary-rules/', TeacherSalaryRulesAPIView.as_view(), name='teacher-salary-rules-list-create'),
    path('v1/finance/teacher-salary-rules/<uuid:pk>/', TeacherSalaryRuleDetailAPIView.as_view(), name='teacher-salary-rule-detail'),

    # Hisoblash tugmasi
    path('v1/finance/teacher-salary/calculate/', TeacherSalaryCalculateAPIView.as_view(), name='teacher-salary-calculate'),
# Barcha to‘lovlar:
# GET /v1/finance/payments/?date_from=2025-10-01&date_to=2025-10-31
# Xarajatlar:
# GET /v1/finance/expenses/?date_from=2025-10-01&date_to=2025-10-31
# Ish haqi qoidalari:
# GET /v1/finance/teacher-salary-rules/
#     qarzdorlar
path('v1/finance/debtors/', DebtorsAPIView.as_view(), name='finance-debtors'),
]




