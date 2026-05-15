from django.urls import path
from .views import ExpenseCategoryViewSet,ExpenseViewSet,BonusViewSet,FineViewSet,EmployeeSalaryPaymentViewSet,FinancialReportAPIView,CashboxViewSet


urlpatterns = [
    # ----------------- KASSA CHIQIMLARI (Expenses) -----------------
    # Xarajat turlari
    path('expense-categories/', ExpenseCategoryViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='expense-category-list'),

    path('expense-categories/<uuid:pk>/', ExpenseCategoryViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='expense-category-detail'),
    # ----------------- CASHBOX (KASSA) -----------------
    path('cashboxes/', CashboxViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='cashbox-list'),

    path('cashboxes/<uuid:pk>/', CashboxViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='cashbox-detail'),
    # Asosiy xarajatlar
    path('expenses/', ExpenseViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='expense-list'),

    path('expenses/<uuid:pk>/', ExpenseViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='expense-detail'),

    # ----------------- XODIMLAR MOLIYASI (HR Finance) -----------------
    # Bonuslar
    path('bonuses/', BonusViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='bonus-list'),

    path('bonuses/<uuid:pk>/', BonusViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='bonus-detail'),

    # Jarimalar
    path('fines/', FineViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='fine-list'),

    path('fines/<uuid:pk>/', FineViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='fine-detail'),

    # Maosh to'lovlari (Admin, SMM va boshqalar)
    path('salary-payments/', EmployeeSalaryPaymentViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='employee-salary-payment-list'),

    path('salary-payments/<uuid:pk>/', EmployeeSalaryPaymentViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='employee-salary-payment-detail'),

    # ----------------- MOLIYAVIY HISOBOT (Reports) -----------------
    # Kassa hisoboti (Tushum, Chiqim, Sof foyda)
    path('report/', FinancialReportAPIView.as_view(), name='financial-report'),
]





