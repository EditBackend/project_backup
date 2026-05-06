from django.urls import path, include
from rest_framework.routers import DefaultRouter
from academics.views.student import (
    StudentViewSet, TalabalarMalumotView, StudentAddPaymentView, StudentLeaveFreezeView
)

router = DefaultRouter()
router.register(r'students', StudentViewSet, basename='student')

urlpatterns = [
    path('', include(router.urls)),

    # Umumiy ro'yxat (Frontend Table uchun optimallashtirilgan)
    path('students-info/', TalabalarMalumotView.as_view(), name='students-info'),

    # To'lov qabul qilish
    path('students/<uuid:student_id>/add-payment/', StudentAddPaymentView.as_view(), name='student-add-payment'),

    # Guruhdan chiqish yoki Muzlatish (action: 'leave' yoki 'freeze')
    path('students/action/<str:action>/', StudentLeaveFreezeView.as_view(), name='student-leave-freeze'),
]