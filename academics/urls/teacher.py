from django.urls import path, include
from rest_framework.routers import DefaultRouter
from academics.views.teacher_salary import (
    TeacherSalaryRulesViewSet,
    TeacherSalaryCalculationsViewSet,
    TeacherSalaryPaymentsViewSet
)

router = DefaultRouter()

# Ustoz oyliklari va qoidalari uchun routerlar
router.register(r'teacher-salary-rules', TeacherSalaryRulesViewSet, basename='salary-rules')
router.register(r'teacher-salary-calculations', TeacherSalaryCalculationsViewSet, basename='salary-calc')
router.register(r'teacher-salary-payments', TeacherSalaryPaymentsViewSet, basename='salary-payments')

urlpatterns = [
    path('', include(router.urls)),
]