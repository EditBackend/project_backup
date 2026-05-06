from django.urls import path
from .views import (
    StudentDebtorsReportAPIView,
    StudentChurnReportAPIView,
    CRMConversionReportAPIView
)

urlpatterns = [
    # Qarzdorlar hisoboti
    path('debtors/', StudentDebtorsReportAPIView.as_view(), name='report-debtors'),

    # Ketgan o'quvchilar (Churn) hisoboti
    path('student-churn/', StudentChurnReportAPIView.as_view(), name='report-churn'),

    # Marketing va Sotuv konversiyasi
    path('crm-conversion/', CRMConversionReportAPIView.as_view(), name='report-crm-conversion'),
]