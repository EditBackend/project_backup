from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Sum
from datetime import date
from django_filters.rest_framework import DjangoFilterBackend

from audit.models import AuditLog, AuditAction, AuditEntityType
from .models import ExpenseCategory, Expense, Bonus, Fine, EmployeeSalaryPayment
from .serializers import (
    ExpenseCategorySerializer, ExpenseSerializer,
    BonusSerializer, FineSerializer, EmployeeSalaryPaymentSerializer
)
# Talaba to'lovlari (Kirim) ni hisoblash uchun Academics dan import qilamiz
from academics.models import StudentTransaction

def _log_audit(request, entity_type, entity_id, action, new_data=None):
    AuditLog.objects.create(
        organization=request.user.organization,
        branch=getattr(request.user, 'branch', None),
        created_by=request.user,
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        new_data=new_data
    )

class BaseFinanceViewSet(viewsets.ModelViewSet):
    """ Tashkilot ma'lumotlarini ajratib beruvchi Asosiy ViewSet """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        if not self.request.user.organization:
            return self.queryset.none()
        return self.queryset.filter(organization=self.request.user.organization).order_by('-created_at')

    def perform_create(self, serializer):
        return serializer.save(
            organization=self.request.user.organization,
            branch=getattr(self.request.user, 'branch', None),
            created_by=self.request.user
        )

# ----------------- KASSA CHIQIMLARI -----------------
class ExpenseCategoryViewSet(BaseFinanceViewSet):
    queryset = ExpenseCategory.objects.all()
    serializer_class = ExpenseCategorySerializer

class ExpenseViewSet(BaseFinanceViewSet):
    queryset = Expense.objects.select_related('category').all()
    serializer_class = ExpenseSerializer
    filterset_fields = ['category', 'payment_method']

    def perform_create(self, serializer):
        expense = super().perform_create(serializer)
        _log_audit(self.request, AuditEntityType.OTHER, expense.id, AuditAction.CREATE,
                   {"action": "Xarajat", "amount": str(expense.amount), "category": getattr(expense.category, 'name', '')})

# ----------------- XODIMLAR MOLIYASI -----------------
class BonusViewSet(BaseFinanceViewSet):
    queryset = Bonus.objects.all()
    serializer_class = BonusSerializer

class FineViewSet(BaseFinanceViewSet):
    queryset = Fine.objects.all()
    serializer_class = FineSerializer

class EmployeeSalaryPaymentViewSet(BaseFinanceViewSet):
    queryset = EmployeeSalaryPayment.objects.all()
    serializer_class = EmployeeSalaryPaymentSerializer

    def perform_create(self, serializer):
        payment = super().perform_create(serializer)
        _log_audit(self.request, AuditEntityType.PAYMENT, payment.id, AuditAction.CREATE,
                   {"action": "Xodim maoshi", "amount": str(payment.amount)})

# =================================================================
# SOF FOYDA VA UMUMIY MOLIYAVIY HISOBOT (JONLI HISOBLASH)
# =================================================================
class FinancialReportAPIView(APIView):
    """ Kassa hisoboti: Tushumlar, Chiqimlar va Sof Foyda """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        org = request.user.organization
        start_date = request.GET.get('start_date', date.today().replace(day=1).isoformat())
        end_date = request.GET.get('end_date', date.today().isoformat())

        # 1. JAMI TUSHUMLAR (Talabalar qilgan to'lovlar)
        total_income = StudentTransaction.objects.filter(
            organization=org,
            transaction_type='payment',
            transaction_date__date__range=[start_date, end_date]
        ).aggregate(total=Sum('amount'))['total'] or 0

        # 2. JAMI XARAJATLAR (Arenda, svet, qog'oz va h.k.)
        total_expense = Expense.objects.filter(
            organization=org,
            expense_date__range=[start_date, end_date]
        ).aggregate(total=Sum('amount'))['total'] or 0

        # 3. XODIMLAR MAOSHLARI (O'qituvchilar va Boshqa xodimlar)
        staff_salary = EmployeeSalaryPayment.objects.filter(
            organization=org, payment_date__range=[start_date, end_date]
        ).aggregate(total=Sum('amount'))['total'] or 0

        total_outcomes = total_expense + staff_salary
        net_profit = total_income - total_outcomes

        return Response({
            "period": f"{start_date} dan {end_date} gacha",
            "income": {
                "student_payments": float(total_income),
                "total_income": float(total_income)
            },
            "outcomes": {
                "expenses": float(total_expense),
                "salaries": float(staff_salary),
                "total_outcomes": float(total_outcomes)
            },
            "net_profit": float(net_profit),
            "status": "Foyda" if net_profit >= 0 else "Zarar"
        })


# from rest_framework import viewsets
# from rest_framework.decorators import action
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.views import APIView
# from drf_spectacular.utils import extend_schema, OpenApiParameter
# from django.db.models import Sum, Q, Count
# from datetime import datetime, timedelta
# from rest_framework import status
# from django.db.models import Avg
# from django.db.models.functions import TruncDate, ExtractHour
# from django.db.models.functions import TruncMonth
#
# from audit.models import AuditLog
# from .models import (
#     ExpenseCategory, Expenses, MonthlyIncome, Payment, Sale,
#     DetailedExpense, ExpenseSubcategory, Bonus, Fine, Salary
# )
# from .serializers import (
#     ExpenseCategorySerializer, ExpensesSerializer, MonthlyIncomeSerializer,
#     PaymentSerializer, SaleSerializer, DetailedExpenseSerializer,
#     ExpenseSubcategorySerializer, BulkSalaryConfigSerializer, PayPeriodSerializer,
#     CRMLeadSerializer, WithdrawalListSerializer,
#     BonusSerializer, FineSerializer, SalarySerializer,
#     TeacherSalaryRulesSerializer, TeacherSalaryPaymentsSerializer,
#     TeacherSalaryCalculationsSerializer,
#      LeaveReasonSerializer,
#     StudentGroupLeavesSerializer
# )
# from accounts.models import Employee
# from academics.models.group import Course, Group, GroupTeacher
# from academics.models.teacher import TeacherSalaryRules, TeacherSalaryPayments, TeacherSalaryCalculations
# from academics.models.student import Student, StudentGroup, StudentGroupLeaves, LeaveReason
# from crm.models import (
#     CRMSource, CRMLead, CRMActivity,
#     CRMLeadsHistory, CRMLostReason, CRMLeadLost, CRMLeadNotes,
# )
#
#
# # ─── AuditLog helper ─────────────────────────────────────────────
#
# def _log(entity_type, entity_id, action, old_data, new_data, user):
#     try:
#         employee = user.employee if hasattr(user, 'employee') else None
#         AuditLog.objects.create(
#             entity_type=entity_type,
#             entity_id=entity_id,
#             action=action,
#             old_data=old_data,
#             new_action=new_data,
#             performed_by=employee,
#             performed_by_role=employee.position if employee else '',
#         )
#     except Exception:
#         pass
#
#
# # ════════════════════════════════════════════════════════════════
# #  EXPENSE CATEGORY
# # ════════════════════════════════════════════════════════════════
#
# @extend_schema(tags=["ExpenseCategory - Harajatlar kategoriyasini ko'rish"])
# class ExpenseCategoryViewSet(viewsets.ModelViewSet):
#     queryset           = ExpenseCategory.objects.all()
#     serializer_class   = ExpenseCategorySerializer
#     permission_classes = [IsAuthenticated]
#
#     def perform_create(self, serializer):
#         obj = serializer.save()
#         _log('other', obj.id, 'create', None, {
#             'action': 'Harajat kategoriyasi yaratildi',
#             'name':   obj.name,
#         }, self.request.user)
#
#     def perform_update(self, serializer):
#         old = {'name': serializer.instance.name}
#         obj = serializer.save()
#         _log('other', obj.id, 'update', old, {'name': obj.name}, self.request.user)
#
#     def perform_destroy(self, instance):
#         _log('other', instance.id, 'delete', {'name': instance.name}, None, self.request.user)
#         instance.delete()
#
#
# # ════════════════════════════════════════════════════════════════
# #  EXPENSES
# # ════════════════════════════════════════════════════════════════
#
# @extend_schema(tags=["Expenses"])
# class ExpensesViewSet(viewsets.ModelViewSet):
#     queryset           = Expenses.objects.select_related('category').all()
#     serializer_class   = ExpensesSerializer
#     permission_classes = [IsAuthenticated]
#
#     def get_queryset(self):
#         queryset   = super().get_queryset()
#         category   = self.request.query_params.get('category')
#         start_date = self.request.query_params.get('start_date')
#         end_date   = self.request.query_params.get('end_date')
#         search     = self.request.query_params.get('search')
#
#         if category:
#             queryset = queryset.filter(category_id=category)
#         if start_date:
#             queryset = queryset.filter(expense_date__gte=start_date)
#         if end_date:
#             queryset = queryset.filter(expense_date__lte=end_date)
#         if search:
#             queryset = queryset.filter(
#                 Q(comment__icontains=search) | Q(category__name__icontains=search)
#             )
#         return queryset
#
#     def perform_create(self, serializer):
#         obj = serializer.save()
#         _log('other', obj.id, 'create', None, {
#             'action':       'Harajat yaratildi',
#             'amount':       str(obj.amount),
#             'category_id':  str(obj.category_id),
#             'expense_date': str(obj.expense_date),
#         }, self.request.user)
#
#     def perform_update(self, serializer):
#         old = {'amount': str(serializer.instance.amount), 'comment': serializer.instance.comment}
#         obj = serializer.save()
#         _log('other', obj.id, 'update', old, {
#             'amount':  str(obj.amount),
#             'comment': obj.comment,
#         }, self.request.user)
#
#     def perform_destroy(self, instance):
#         _log('other', instance.id, 'delete', {
#             'amount': str(instance.amount), 'expense_date': str(instance.expense_date)
#         }, None, self.request.user)
#         instance.delete()
#
#     @extend_schema(parameters=[
#         OpenApiParameter('year', int), OpenApiParameter('month', int),
#     ])
#     @action(detail=False, methods=['get'])
#     def monthly_summary(self, request):
#         year  = request.query_params.get('year', datetime.now().year)
#         month = request.query_params.get('month', datetime.now().month)
#
#         total = self.queryset.filter(
#             expense_date__year=year, expense_date__month=month
#         ).aggregate(total=Sum('amount'))['total'] or 0
#
#         by_category = self.queryset.filter(
#             expense_date__year=year, expense_date__month=month
#         ).values('category__name').annotate(total=Sum('amount'))
#
#         return Response({'year': year, 'month': month,
#                          'total_expenses': total, 'by_category': list(by_category)})
#
#
# # ════════════════════════════════════════════════════════════════
# #  MONTHLY INCOME
# # ════════════════════════════════════════════════════════════════
#
# @extend_schema(tags=["MonthlyIncome"])
# class MonthlyIncomeViewSet(viewsets.ModelViewSet):
#     queryset           = MonthlyIncome.objects.all()
#     serializer_class   = MonthlyIncomeSerializer
#     permission_classes = [IsAuthenticated]
#
#     def perform_create(self, serializer):
#         obj = serializer.save()
#         _log('other', obj.id, 'create', None, {
#             'action':       'Oylik daromad yaratildi',
#             'total_amount': str(obj.total_amount),
#             'month':        str(obj.month),
#         }, self.request.user)
#
#     def perform_update(self, serializer):
#         old = {'total_amount': str(serializer.instance.total_amount)}
#         obj = serializer.save()
#         _log('other', obj.id, 'update', old, {'total_amount': str(obj.total_amount)}, self.request.user)
#
#     def perform_destroy(self, instance):
#         _log('other', instance.id, 'delete', {
#             'total_amount': str(instance.total_amount), 'month': str(instance.month)
#         }, None, self.request.user)
#         instance.delete()
#
#     @action(detail=True, methods=['get'])
#     def net_profit(self, request, pk=None):
#         income   = self.get_object()
#         expenses = Expenses.objects.filter(
#             expense_date__year=income.month.year,
#             expense_date__month=income.month.month,
#         ).aggregate(total=Sum('amount'))['total'] or 0
#
#         return Response({
#             'income':     income.total_amount,
#             'expenses':   expenses,
#             'net_profit': income.total_amount - expenses,
#         })
#
#
# # ════════════════════════════════════════════════════════════════
# #  PAYMENT
# # ════════════════════════════════════════════════════════════════
#
# @extend_schema(tags=["Payment"])
# class PaymentViewSet(viewsets.ModelViewSet):
#     queryset           = Payment.objects.all()
#     serializer_class   = PaymentSerializer
#     permission_classes = [IsAuthenticated]
#
#     def perform_create(self, serializer):
#         obj = serializer.save()
#         _log('other', obj.id, 'create', None, {
#             'action': 'To\'lov turi yaratildi', 'name': obj.name,
#         }, self.request.user)
#
#     def perform_update(self, serializer):
#         old = {'name': serializer.instance.name, 'is_active': serializer.instance.is_active}
#         obj = serializer.save()
#         _log('other', obj.id, 'update', old, {
#             'name': obj.name, 'is_active': obj.is_active,
#         }, self.request.user)
#
#     def perform_destroy(self, instance):
#         _log('other', instance.id, 'delete', {'name': instance.name}, None, self.request.user)
#         instance.delete()
#
#
# # ════════════════════════════════════════════════════════════════
# #  SALE
# # ════════════════════════════════════════════════════════════════
#
# @extend_schema(tags=["Sales"])
# class SaleViewSet(viewsets.ModelViewSet):
#     queryset           = Sale.objects.all()
#     serializer_class   = SaleSerializer
#     permission_classes = [IsAuthenticated]
#
#     def get_queryset(self):
#         queryset = super().get_queryset()
#         date     = self.request.query_params.get('date')
#         month    = self.request.query_params.get('month')
#         debt     = self.request.query_params.get('debt')
#         course   = self.request.query_params.get('course')
#
#         if date:
#             queryset = queryset.filter(sale_date__date=date)
#         if month:
#             queryset = queryset.filter(month=month)
#         if debt == 'true':
#             queryset = queryset.filter(debt_amount__gt=0)
#         if course:
#             queryset = queryset.filter(course__icontains=course)
#         return queryset
#
#     def perform_create(self, serializer):
#         obj = serializer.save()
#         _log('payment', obj.id, 'create', None, {
#             'action':        'Sotuv yaratildi',
#             'customer_name': obj.customer_name,
#             'amount':        str(obj.amount),
#             'debt_amount':   str(obj.debt_amount),
#         }, self.request.user)
#
#     def perform_update(self, serializer):
#         old = {'amount': str(serializer.instance.amount), 'debt_amount': str(serializer.instance.debt_amount)}
#         obj = serializer.save()
#         _log('payment', obj.id, 'update', old, {
#             'amount': str(obj.amount), 'debt_amount': str(obj.debt_amount),
#         }, self.request.user)
#
#     def perform_destroy(self, instance):
#         _log('payment', instance.id, 'delete', {
#             'customer_name': instance.customer_name, 'amount': str(instance.amount),
#         }, None, self.request.user)
#         instance.delete()
#
#     @extend_schema(parameters=[
#         OpenApiParameter('start_month', str), OpenApiParameter('end_month', str),
#     ])
#     @action(detail=False, methods=['get'])
#     def statistics(self, request):
#         start   = request.query_params.get('start_month')
#         end     = request.query_params.get('end_month')
#         queryset = self.queryset
#         if start and end:
#             queryset = queryset.filter(month__range=[start, end])
#
#         total_sales = queryset.aggregate(total=Sum('amount'))['total'] or 0
#         total_debt  = queryset.aggregate(total=Sum('debt_amount'))['total'] or 0
#         monthly     = queryset.values('month').annotate(
#             total=Sum('amount'), debt=Sum('debt_amount')
#         ).order_by('month')
#
#         return Response({
#             'total_sales': total_sales, 'total_paid': total_sales - total_debt,
#             'total_debt': total_debt, 'monthly_breakdown': list(monthly),
#         })
#
#     @action(detail=False, methods=['get'])
#     def active_count(self, request):
#         count = self.queryset.filter(
#             created_at__gte=datetime.now() - timedelta(days=30)
#         ).count()
#         return Response({'active_count': count, 'limit': 500})
#
#
# # ════════════════════════════════════════════════════════════════
# #  EXPENSE SUBCATEGORY
# # ════════════════════════════════════════════════════════════════
#
# @extend_schema(tags=["ExpenseSubcategory"])
# class ExpenseSubcategoryViewSet(viewsets.ModelViewSet):
#     queryset           = ExpenseSubcategory.objects.select_related('category').all()
#     serializer_class   = ExpenseSubcategorySerializer
#     permission_classes = [IsAuthenticated]
#
#     def get_queryset(self):
#         queryset = super().get_queryset()
#         category = self.request.query_params.get('category')
#         etype    = self.request.query_params.get('type')
#         if category:
#             queryset = queryset.filter(category_id=category)
#         if etype:
#             queryset = queryset.filter(type=etype)
#         return queryset
#
#     def perform_create(self, serializer):
#         obj = serializer.save()
#         _log('other', obj.id, 'create', None, {
#             'action': 'Harajat subkategoriyasi yaratildi', 'name': obj.name,
#         }, self.request.user)
#
#     def perform_update(self, serializer):
#         old = {'name': serializer.instance.name}
#         obj = serializer.save()
#         _log('other', obj.id, 'update', old, {'name': obj.name}, self.request.user)
#
#     def perform_destroy(self, instance):
#         _log('other', instance.id, 'delete', {'name': instance.name}, None, self.request.user)
#         instance.delete()
#
#
# # ════════════════════════════════════════════════════════════════
# #  DETAILED EXPENSE
# # ════════════════════════════════════════════════════════════════
#
# @extend_schema(tags=["DetailedExpense"])
# class DetailedExpenseViewSet(viewsets.ModelViewSet):
#     queryset           = DetailedExpense.objects.select_related('subcategory', 'payment_type').all()
#     serializer_class   = DetailedExpenseSerializer
#     permission_classes = [IsAuthenticated]
#
#     def get_queryset(self):
#         queryset    = super().get_queryset()
#         subcategory = self.request.query_params.get('subcategory')
#         start_date  = self.request.query_params.get('start_date')
#         end_date    = self.request.query_params.get('end_date')
#         payment     = self.request.query_params.get('payment')
#
#         if subcategory:
#             queryset = queryset.filter(subcategory_id=subcategory)
#         if start_date:
#             queryset = queryset.filter(date__gte=start_date)
#         if end_date:
#             queryset = queryset.filter(date__lte=end_date)
#         if payment:
#             queryset = queryset.filter(payment_type_id=payment)
#         return queryset
#
#     def perform_create(self, serializer):
#         obj = serializer.save()
#         _log('other', obj.id, 'create', None, {
#             'action': 'Batafsil harajat yaratildi',
#             'amount': str(obj.amount),
#             'date':   str(obj.date),
#         }, self.request.user)
#
#     def perform_update(self, serializer):
#         old = {'amount': str(serializer.instance.amount), 'comment': serializer.instance.comment}
#         obj = serializer.save()
#         _log('other', obj.id, 'update', old, {
#             'amount': str(obj.amount), 'comment': obj.comment,
#         }, self.request.user)
#
#     def perform_destroy(self, instance):
#         _log('other', instance.id, 'delete', {
#             'amount': str(instance.amount), 'date': str(instance.date),
#         }, None, self.request.user)
#         instance.delete()
#
#     @extend_schema(parameters=[OpenApiParameter('year', int), OpenApiParameter('month', int)])
#     @action(detail=False, methods=['get'])
#     def chart_data(self, request):
#         year    = request.query_params.get('year', datetime.now().year)
#         month   = request.query_params.get('month')
#         queryset = self.queryset.filter(date__year=year)
#         if month:
#             queryset = queryset.filter(date__month=month)
#
#         monthly     = queryset.values('date__month').annotate(total=Sum('amount')).order_by('date__month')
#         by_category = queryset.values('subcategory__type').annotate(total=Sum('amount'))
#
#         return Response({'line_chart': list(monthly), 'pie_chart': list(by_category)})
#
#     @action(detail=False, methods=['get'])
#     def directors_summary(self, request):
#         ceo    = self.queryset.filter(comment__icontains='CEO').aggregate(total=Sum('amount'))['total'] or 0
#         filial = self.queryset.filter(comment__icontains='filial').aggregate(total=Sum('amount'))['total'] or 0
#         return Response({'ceo': ceo, 'filial_directors': filial})
#
#
# # ════════════════════════════════════════════════════════════════
# #  BONUS / FINE / SALARY
# # ════════════════════════════════════════════════════════════════
#
# @extend_schema(tags=["Bonus"])
# class BonusViewSet(viewsets.ModelViewSet):
#     queryset           = Bonus.objects.select_related('employee', 'course').all()
#     serializer_class   = BonusSerializer
#     permission_classes = [IsAuthenticated]
#
#     def get_queryset(self):
#         queryset   = super().get_queryset()
#         employee   = self.request.query_params.get('employee')
#         month      = self.request.query_params.get('month')
#         bonus_type = self.request.query_params.get('bonus_type')
#         if employee:
#             queryset = queryset.filter(employee_id=employee)
#         if month:
#             queryset = queryset.filter(month=month)
#         if bonus_type:
#             queryset = queryset.filter(bonus_type=bonus_type)
#         return queryset
#
#     def perform_create(self, serializer):
#         obj = serializer.save()
#         _log('other', obj.id, 'create', None, {
#             'action':      'Bonus yaratildi',
#             'employee_id': str(obj.employee_id),
#             'amount':      str(obj.amount),
#             'bonus_type':  obj.bonus_type,
#             'month':       str(obj.month),
#         }, self.request.user)
#
#     def perform_update(self, serializer):
#         old = {'amount': str(serializer.instance.amount)}
#         obj = serializer.save()
#         _log('other', obj.id, 'update', old, {'amount': str(obj.amount)}, self.request.user)
#
#     def perform_destroy(self, instance):
#         _log('other', instance.id, 'delete', {
#             'employee_id': str(instance.employee_id), 'amount': str(instance.amount),
#         }, None, self.request.user)
#         instance.delete()
#
#
# @extend_schema(tags=["Fine"])
# class FineViewSet(viewsets.ModelViewSet):
#     queryset           = Fine.objects.select_related('employee').all()
#     serializer_class   = FineSerializer
#     permission_classes = [IsAuthenticated]
#
#     def get_queryset(self):
#         queryset   = super().get_queryset()
#         employee   = self.request.query_params.get('employee')
#         start_date = self.request.query_params.get('start_date')
#         end_date   = self.request.query_params.get('end_date')
#         if employee:
#             queryset = queryset.filter(employee_id=employee)
#         if start_date:
#             queryset = queryset.filter(date__gte=start_date)
#         if end_date:
#             queryset = queryset.filter(date__lte=end_date)
#         return queryset
#
#     def perform_create(self, serializer):
#         obj = serializer.save()
#         _log('other', obj.id, 'create', None, {
#             'action':      'Jarima yaratildi',
#             'employee_id': str(obj.employee_id),
#             'amount':      str(obj.amount),
#             'reason':      obj.reason,
#         }, self.request.user)
#
#     def perform_update(self, serializer):
#         old = {'amount': str(serializer.instance.amount), 'reason': serializer.instance.reason}
#         obj = serializer.save()
#         _log('other', obj.id, 'update', old, {
#             'amount': str(obj.amount), 'reason': obj.reason,
#         }, self.request.user)
#
#     def perform_destroy(self, instance):
#         _log('other', instance.id, 'delete', {
#             'employee_id': str(instance.employee_id), 'amount': str(instance.amount),
#         }, None, self.request.user)
#         instance.delete()
#
#
# @extend_schema(tags=["Salary"])
# class SalaryViewSet(viewsets.ModelViewSet):
#     queryset           = Salary.objects.select_related('employee', 'payment_type').all()
#     serializer_class   = SalarySerializer
#     permission_classes = [IsAuthenticated]
#
#     def get_queryset(self):
#         queryset = super().get_queryset()
#         employee = self.request.query_params.get('employee')
#         month    = self.request.query_params.get('month')
#         is_paid  = self.request.query_params.get('is_paid')
#         if employee:
#             queryset = queryset.filter(employee_id=employee)
#         if month:
#             queryset = queryset.filter(month=month)
#         if is_paid:
#             queryset = queryset.filter(is_paid=is_paid == 'true')
#         return queryset
#
#     def perform_create(self, serializer):
#         obj = serializer.save()
#         _log('other', obj.id, 'create', None, {
#             'action':       'Maosh yaratildi',
#             'employee_id':  str(obj.employee_id),
#             'total_amount': str(obj.total_amount),
#             'month':        str(obj.month),
#         }, self.request.user)
#
#     def perform_update(self, serializer):
#         old = {'total_amount': str(serializer.instance.total_amount), 'is_paid': serializer.instance.is_paid}
#         obj = serializer.save()
#         _log('other', obj.id, 'update', old, {
#             'total_amount': str(obj.total_amount), 'is_paid': obj.is_paid,
#         }, self.request.user)
#
#     def perform_destroy(self, instance):
#         _log('other', instance.id, 'delete', {
#             'employee_id': str(instance.employee_id), 'total_amount': str(instance.total_amount),
#         }, None, self.request.user)
#         instance.delete()
#
#     @extend_schema(parameters=[OpenApiParameter('employee_id', int), OpenApiParameter('month', str)])
#     @action(detail=False, methods=['post'])
#     def calculate(self, request):
#         employee_id = request.data.get('employee_id')
#         month       = request.data.get('month')
#         try:
#             employee   = Employee.objects.get(id=employee_id)
#             month_date = datetime.strptime(month, '%Y-%m-%d').date()
#             bonuses    = Bonus.objects.filter(employee=employee, month=month_date).aggregate(total=Sum('amount'))['total'] or 0
#             fines      = Fine.objects.filter(employee=employee, date__year=month_date.year, date__month=month_date.month).aggregate(total=Sum('amount'))['total'] or 0
#
#             salary, created = Salary.objects.get_or_create(
#                 employee=employee, month=month_date,
#                 defaults={'base_amount': employee.base_salary, 'bonus_amount': bonuses, 'fine_amount': fines}
#             )
#             if not created:
#                 salary.bonus_amount = bonuses
#                 salary.fine_amount  = fines
#                 salary.save()
#
#             _log('other', salary.id, 'create' if created else 'update', None, {
#                 'action':       'Maosh hisoblandi',
#                 'employee_id':  str(employee_id),
#                 'month':        str(month_date),
#                 'bonus_amount': str(bonuses),
#                 'fine_amount':  str(fines),
#             }, request.user)
#
#             return Response(SalarySerializer(salary).data)
#         except Employee.DoesNotExist:
#             return Response({'error': 'Xodim topilmadi'}, status=404)
#
#     @action(detail=False, methods=['get'])
#     def summary(self, request):
#         month    = request.query_params.get('month')
#         queryset = self.queryset
#         if month:
#             queryset = queryset.filter(month=month)
#
#         total_paid   = queryset.filter(is_paid=True).aggregate(total=Sum('total_amount'))['total'] or 0
#         total_unpaid = queryset.filter(is_paid=False).aggregate(total=Sum('total_amount'))['total'] or 0
#         by_employee  = queryset.values('employee__full_name').annotate(
#             total=Sum('total_amount'), bonuses=Sum('bonus_amount'), fines=Sum('fine_amount')
#         )
#         return Response({'total_paid': total_paid, 'total_unpaid': total_unpaid, 'by_employee': list(by_employee)})
#
#
# # ════════════════════════════════════════════════════════════════
# #  TEACHER SALARY RULES
# # ════════════════════════════════════════════════════════════════
#
# @extend_schema(tags=["TeacherSalaryRules"])
# class TeacherSalaryRulesViewSet(viewsets.ModelViewSet):
#     queryset           = TeacherSalaryRules.objects.select_related('teacher').all()
#     serializer_class   = TeacherSalaryRulesSerializer
#     permission_classes = [IsAuthenticated]
#
#     def get_queryset(self):
#         queryset   = super().get_queryset()
#         teacher    = self.request.query_params.get('teacher')
#         is_active  = self.request.query_params.get('is_active')
#         start_date = self.request.query_params.get('start_date')
#         end_date   = self.request.query_params.get('end_date')
#
#         if teacher:
#             queryset = queryset.filter(teacher_id=teacher)
#         if is_active == 'true':
#             today    = datetime.now().date()
#             queryset = queryset.filter(effective_from__lte=today, effective_to__gte=today)
#         if start_date:
#             queryset = queryset.filter(effective_from__gte=start_date)
#         if end_date:
#             queryset = queryset.filter(effective_to__lte=end_date)
#         return queryset
#
#     def perform_create(self, serializer):
#         obj = serializer.save()
#         _log('other', obj.id, 'create', None, {
#             'action':              "O'qituvchi maosh qoidasi yaratildi",
#             'teacher_id':          str(obj.teacher_id),
#             'percent_per_student': str(obj.percent_per_student),
#             'fixed_bonus':         str(obj.fixed_bonus),
#             'effective_from':      str(obj.effective_from),
#             'effective_to':        str(obj.effective_to),
#         }, self.request.user)
#
#     def perform_update(self, serializer):
#         old = {'percent_per_student': str(serializer.instance.percent_per_student),
#                'fixed_bonus': str(serializer.instance.fixed_bonus)}
#         obj = serializer.save()
#         _log('other', obj.id, 'update', old, {
#             'percent_per_student': str(obj.percent_per_student),
#             'fixed_bonus':         str(obj.fixed_bonus),
#         }, self.request.user)
#
#     def perform_destroy(self, instance):
#         _log('other', instance.id, 'delete', {
#             'teacher_id': str(instance.teacher_id),
#         }, None, self.request.user)
#         instance.delete()
#
#     @action(detail=False, methods=['post'])
#     def bulk_create(self, request):
#         percent = request.data.get('percent_per_student')
#         fixed_bonus = request.data.get('fixed_bonus')
#         effective_from = request.data.get('effective_from')
#         effective_to = request.data.get('effective_to')
#
#         # 1. Ma'lumotlar to'liqligini tekshirish
#         if not all([percent, fixed_bonus, effective_from, effective_to]):
#             return Response({'error': 'Barcha maydonlar (percent, fixed_bonus, dates) majburiy!'}, status=400)
#
#         # 2. O'qituvchilarni qidirish (Lotin/Kirill variantlari bilan)
#         teachers = Employee.objects.filter(
#             Q(position__icontains="o'qituvchi") |
#             Q(position__icontains="o‘qituvchi") |
#             Q(position__icontains="teacher")
#         )
#
#         if not teachers.exists():
#             return Response({'error': 'Belgilangan lavozimdagi o\'qituvchilar topilmadi.'}, status=404)
#
#         created_count = 0
#
#         try:
#             with transaction.atomic(): # Xatolik bo'lsa barchasini qaytaradi
#                 for teacher in teachers:
#                     # 3. Har bir xodimning o'z branch va organization ID'larini olish
#                     # TeacherSalaryRules BaseModel'dan meros olgani uchun bular shart!
#                     TeacherSalaryRules.objects.create(
#                         teacher=teacher,
#                         percent_per_student=percent,
#                         fixed_bonus=fixed_bonus,
#                         effective_from=effective_from,
#                         effective_to=effective_to,
#                         branch_id=teacher.branch_id,       # MUHIM
#                         organization_id=teacher.organization_id # MUHIM
#                     )
#                     created_count += 1
#
#                 # 4. AuditLog yozish
#                 _log('other', None, 'create', None, {
#                     'action': 'Bulk teacher salary rules yaratildi',
#                     'created_count': created_count,
#                     'percent_per_student': str(percent),
#                     'fixed_bonus': str(fixed_bonus),
#                     'period': f"{effective_from} - {effective_to}"
#                 }, request.user)
#
#         except IntegrityError as e:
#             return Response({'error': f'Ma\'lumotlar bazasiga saqlashda xato: {str(e)}'}, status=400)
#         except Exception as e:
#             return Response({'error': f'Kutilmagan xatolik: {str(e)}'}, status=500)
#
#         return Response({
#             'success': True,
#             'message': f'{created_count} ta ustoz uchun qoidalar muvaffaqiyatli yaratildi.',
#             'data': {
#                 'percent': percent,
#                 'fixed_bonus': fixed_bonus,
#                 'effective_from': effective_from,
#                 'effective_to': effective_to
#             }
#         }, status=201)
#
#     @extend_schema(request=PayPeriodSerializer, responses={200: TeacherSalaryRulesSerializer(many=True)})
#     @action(detail=False, methods=['post'])
#     def get_by_period(self, request):
#         serializer = PayPeriodSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         start = serializer.validated_data['start_date']
#         end   = serializer.validated_data['end_date']
#         rules = self.queryset.filter(effective_from__lte=end, effective_to__gte=start)
#         return Response({'period': {'start_date': start, 'end_date': end},
#                          'count': rules.count(),
#                          'rules': TeacherSalaryRulesSerializer(rules, many=True).data})
#
#     @extend_schema(request=BulkSalaryConfigSerializer, responses={200: {'type': 'object'}})
#     @action(detail=False, methods=['post'])
#     def configure_period(self, request):
#         serializer = BulkSalaryConfigSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         data = serializer.validated_data
#
#         if data['apply_to_all']:
#             # O'qituvchilarni kengaytirilgan filtr bilan olish
#             teachers = Employee.objects.filter(
#                 Q(position__icontains="o'qituvchi") | Q(position__icontains="o‘qituvchi")
#             )
#             created = []
#             with transaction.atomic():
#                 for teacher in teachers:
#                     rule = TeacherSalaryRules.objects.create(
#                         teacher=teacher,
#                         percent_per_student=data['percent_per_student'],
#                         fixed_bonus=data['fixed_bonus'],
#                         effective_from=data['start_date'],
#                         effective_to=data['end_date'],
#                         # MANA BU QATORLARNI QO'SHING
#                         branch_id=teacher.branch_id,
#                         organization_id=teacher.organization_id
#                     )
#                     created.append(rule)
#             _log('other', None, 'create', None, {
#                 'action':              'configure_period - bulk sozlama',
#                 'created_count':       len(created),
#                 'percent_per_student': str(percent),
#                 'fixed_bonus':         str(fixed),
#                 'period':              f'{start} - {end}',
#             }, request.user)
#
#             return Response({'message': f'{len(created)} ta ustoz uchun sozlamalar yaratildi',
#                              'period': f'{start} - {end}', 'percent_per_student': percent,
#                              'fixed_bonus': fixed, 'created_count': len(created)})
#         return Response({'success': True, 'created_count': len(created)})
#
#     @action(detail=False, methods=['get'])
#     def active_periods(self, request):
#         periods = self.queryset.values('effective_from', 'effective_to').distinct().order_by('-effective_from')
#         result  = []
#         for period in periods:
#             start = period['effective_from']
#             end   = period['effective_to']
#             count = self.queryset.filter(effective_from=start, effective_to=end).count()
#             result.append({
#                 'start_date':    start,
#                 'end_date':      end,
#                 'name':          f"{start.strftime('%B %Y')} - {end.strftime('%B %Y')}",
#                 'teacher_count': count,
#                 'is_active':     start <= datetime.now().date() <= end,
#             })
#         return Response(result)
#
#     @extend_schema(parameters=[OpenApiParameter('start_date', str), OpenApiParameter('end_date', str)])
#     @action(detail=False, methods=['get'])
#     def period_summary(self, request):
#         start = request.query_params.get('start_date')
#         end   = request.query_params.get('end_date')
#         if not start or not end:
#             return Response({'error': 'start_date va end_date majburiy'}, status=400)
#
#         rules        = self.queryset.filter(effective_from__lte=end, effective_to__gte=start)
#         calculations = TeacherSalaryCalculations.objects.filter(calculated_at__range=[start, end])
#         payments     = TeacherSalaryPayments.objects.filter(payment_date__range=[start, end])
#
#         total_calculated = calculations.aggregate(total=Sum('total_amount'))['total'] or 0
#         total_paid       = payments.aggregate(total=Sum('amount'))['total'] or 0
#
#         return Response({'period': {'start': start, 'end': end}, 'active_rules': rules.count(),
#                          'total_calculated': total_calculated, 'total_paid': total_paid,
#                          'debt': total_calculated - total_paid,
#                          'teachers_with_rules': rules.values('teacher').distinct().count()})
#
#
# # ════════════════════════════════════════════════════════════════
# #  TEACHER SALARY PAYMENTS
# # ════════════════════════════════════════════════════════════════
#
# @extend_schema(tags=["TeacherSalaryPayments"])
# class TeacherSalaryPaymentsViewSet(viewsets.ModelViewSet):
#     queryset           = TeacherSalaryPayments.objects.select_related('teacher').all()
#     serializer_class   = TeacherSalaryPaymentsSerializer
#     permission_classes = [IsAuthenticated]
#
#     def get_queryset(self):
#         queryset     = super().get_queryset()
#         teacher      = self.request.query_params.get('teacher')
#         start_date   = self.request.query_params.get('start_date')
#         end_date     = self.request.query_params.get('end_date')
#         payment_type = self.request.query_params.get('payment_type')
#         if teacher:
#             queryset = queryset.filter(teacher_id=teacher)
#         if start_date:
#             queryset = queryset.filter(payment_date__gte=start_date)
#         if end_date:
#             queryset = queryset.filter(payment_date__lte=end_date)
#         if payment_type:
#             queryset = queryset.filter(payment_type=payment_type)
#         return queryset
#
#     def perform_create(self, serializer):
#         obj = serializer.save()
#         _log('other', obj.id, 'create', None, {
#             'action':       "O'qituvchiga maosh to'landi",
#             'teacher_id':   str(obj.teacher_id),
#             'amount':       str(obj.amount),
#             'payment_date': str(obj.payment_date),
#             'payment_type': obj.payment_type,
#         }, self.request.user)
#
#     def perform_update(self, serializer):
#         old = {'amount': str(serializer.instance.amount)}
#         obj = serializer.save()
#         _log('other', obj.id, 'update', old, {'amount': str(obj.amount)}, self.request.user)
#
#     def perform_destroy(self, instance):
#         _log('other', instance.id, 'delete', {
#             'teacher_id': str(instance.teacher_id), 'amount': str(instance.amount),
#         }, None, self.request.user)
#         instance.delete()
#
#     @action(detail=False, methods=['get'])
#     def summary(self, request):
#         teacher  = request.query_params.get('teacher')
#         month    = request.query_params.get('month')
#         queryset = self.queryset
#         if teacher:
#             queryset = queryset.filter(teacher_id=teacher)
#         if month:
#             queryset = queryset.filter(payment_date__month=month)
#         total  = queryset.aggregate(total=Sum('amount'))['total'] or 0
#         by_type = queryset.values('payment_type').annotate(total=Sum('amount'))
#         return Response({'total_paid': total, 'by_payment_type': list(by_type)})
#
#
# # ════════════════════════════════════════════════════════════════
# #  TEACHER SALARY CALCULATIONS
# # ════════════════════════════════════════════════════════════════
#
# @extend_schema(tags=["TeacherSalaryCalculations"])
# class TeacherSalaryCalculationsViewSet(viewsets.ModelViewSet):
#     queryset           = TeacherSalaryCalculations.objects.select_related('teacher', 'group').all()
#     serializer_class   = TeacherSalaryCalculationsSerializer
#     permission_classes = [IsAuthenticated]
#
#     def get_queryset(self):
#         queryset = super().get_queryset()
#         teacher  = self.request.query_params.get('teacher')
#         group    = self.request.query_params.get('group')
#         month    = self.request.query_params.get('month')
#         if teacher:
#             queryset = queryset.filter(teacher_id=teacher)
#         if group:
#             queryset = queryset.filter(group_id=group)
#         if month:
#             queryset = queryset.filter(month=month)
#         return queryset
#
#     def perform_create(self, serializer):
#         obj = serializer.save()
#         _log('other', obj.id, 'create', None, {
#             'action':       'Maosh hisoblandi',
#             'teacher_id':   str(obj.teacher_id),
#             'total_amount': str(obj.total_amount),
#             'month':        str(obj.month),
#         }, self.request.user)
#
#     def perform_destroy(self, instance):
#         _log('other', instance.id, 'delete', {
#             'teacher_id': str(instance.teacher_id), 'month': str(instance.month),
#         }, None, self.request.user)
#         instance.delete()
#
#     @action(detail=False, methods=['post'])
#     def calculate(self, request):
#         teacher_id    = request.data.get('teacher_id')
#         group_id      = request.data.get('group_id')
#         month         = request.data.get('month')
#         student_count = request.data.get('student_count')
#
#         if not all([teacher_id, group_id, month, student_count]):
#             return Response({'error': 'Barcha maydonlar majburiy'}, status=400)
#
#         try:
#             teacher = Employee.objects.get(id=teacher_id)
#             today   = datetime.now().date()
#             rule    = TeacherSalaryRules.objects.filter(
#                 teacher=teacher, effective_from__lte=today, effective_to__gte=today
#             ).first()
#
#             if not rule:
#                 return Response({'error': 'Aktiv qoida topilmadi'}, status=404)
#
#             percent = rule.percent_per_student
#             total   = (student_count * percent) + rule.fixed_bonus
#
#             calculation = TeacherSalaryCalculations.objects.create(
#                 teacher_id=teacher_id, group_id=group_id, month=month,
#                 student_count=student_count, percent=percent,
#                 total_amount=total, calculated_at=today,
#             )
#
#             _log('other', calculation.id, 'create', None, {
#                 'action':       'calculate action - maosh hisoblandi',
#                 'teacher_id':   str(teacher_id),
#                 'total_amount': str(total),
#                 'month':        str(month),
#             }, request.user)
#
#             return Response(TeacherSalaryCalculationsSerializer(calculation).data)
#         except Employee.DoesNotExist:
#             return Response({'error': 'Ustoz topilmadi'}, status=404)
#
#     @action(detail=False, methods=['get'])
#     def monthly_report(self, request):
#         teacher = request.query_params.get('teacher')
#         month   = request.query_params.get('month')
#         if not month:
#             return Response({'error': 'month majburiy'}, status=400)
#
#         queryset = self.queryset.filter(month=month)
#         if teacher:
#             queryset = queryset.filter(teacher_id=teacher)
#
#         total_calculated = queryset.aggregate(total=Sum('total_amount'))['total'] or 0
#         total_students   = queryset.aggregate(total=Sum('student_count'))['total'] or 0
#         by_teacher       = queryset.values('teacher__full_name').annotate(
#             total=Sum('total_amount'), students=Sum('student_count'), groups=Count('group')
#         )
#
#         paid_qs = TeacherSalaryPayments.objects.filter(payment_date__month=month)
#         if teacher:
#             paid_qs = paid_qs.filter(teacher_id=teacher)
#         paid = paid_qs.aggregate(total=Sum('amount'))['total'] or 0
#
#         return Response({'month': month, 'total_calculated': total_calculated,
#                          'total_paid': paid, 'debt': total_calculated - paid,
#                          'total_students': total_students, 'by_teacher': list(by_teacher)})
#
#
# # ════════════════════════════════════════════════════════════════
# #  QARZDORLAR
# # ════════════════════════════════════════════════════════════════
#
# @extend_schema(tags=["Debts - Qarzdorlar"])
# class StudentDebtsViewSet(viewsets.ReadOnlyModelViewSet):
#     queryset         = Sale.objects.filter(debt_amount__gt=0)
#     serializer_class = SaleSerializer
#
#     def get_queryset(self):
#         queryset   = super().get_queryset()
#         name       = self.request.query_params.get('name')
#         min_debt   = self.request.query_params.get('min_debt')
#         max_debt   = self.request.query_params.get('max_debt')
#         start_date = self.request.query_params.get('start_date')
#         end_date   = self.request.query_params.get('end_date')
#         course     = self.request.query_params.get('course')
#
#         if name:
#             queryset = queryset.filter(customer_name__icontains=name)
#         if min_debt:
#             queryset = queryset.filter(debt_amount__gte=min_debt)
#         if max_debt:
#             queryset = queryset.filter(debt_amount__lte=max_debt)
#         if start_date:
#             queryset = queryset.filter(sale_date__gte=start_date)
#         if end_date:
#             queryset = queryset.filter(sale_date__lte=end_date)
#         if course:
#             queryset = queryset.filter(course__icontains=course)
#         return queryset.order_by('-debt_amount')
#
#     @action(detail=False, methods=['get'])
#     def summary(self, request):
#         queryset     = self.get_queryset()
#         total_debt   = queryset.aggregate(total=Sum('debt_amount'))['total'] or 0
#         total_amount = queryset.aggregate(total=Sum('amount'))['total'] or 0
#         by_course    = queryset.values('course').annotate(
#             total_debt=Sum('debt_amount'), count=Count('id')
#         ).order_by('-total_debt')
#         return Response({'total_debt': total_debt, 'debtors_count': queryset.count(),
#                          'total_amount': total_amount, 'paid_amount': total_amount - total_debt,
#                          'by_course': list(by_course)})
#
#
# @extend_schema(tags=["Debts - Qarzdorlar"])
# class TeacherDebtsViewSet(viewsets.ViewSet):
#     def list(self, request):
#         name     = request.query_params.get('name')
#         month    = request.query_params.get('month')
#         min_debt = request.query_params.get('min_debt')
#         teachers = Employee.objects.filter(position__icontains="o'qituvchi")
#         debts    = []
#
#         for teacher in teachers:
#             if name and name.lower() not in teacher.full_name.lower():
#                 continue
#
#             calculated_qs = TeacherSalaryCalculations.objects.filter(teacher=teacher)
#             paid_qs       = TeacherSalaryPayments.objects.filter(teacher=teacher)
#             if month:
#                 calculated_qs = calculated_qs.filter(month=month)
#                 month_date    = datetime.strptime(month, '%Y-%m-%d')
#                 paid_qs       = paid_qs.filter(
#                     payment_date__year=month_date.year, payment_date__month=month_date.month
#                 )
#
#             calculated = calculated_qs.aggregate(total=Sum('total_amount'))['total'] or 0
#             paid       = paid_qs.aggregate(total=Sum('amount'))['total'] or 0
#             debt       = calculated - paid
#
#             if debt > 0:
#                 if min_debt and debt < float(min_debt):
#                     continue
#                 debts.append({
#                     'teacher_id':        teacher.id,
#                     'teacher_name':      teacher.full_name,
#                     'calculated_amount': calculated,
#                     'paid_amount':       paid,
#                     'debt_amount':       debt,
#                     'month':             month or 'Barchasi',
#                 })
#
#         debts.sort(key=lambda x: x['debt_amount'], reverse=True)
#         return Response(debts)
#
#     @action(detail=False, methods=['get'])
#     def summary(self, request):
#         month            = request.query_params.get('month')
#         teachers         = Employee.objects.filter(position__icontains="o'qituvchi")
#         total_calculated = total_paid = 0
#         debtors          = []
#
#         for teacher in teachers:
#             calculated_qs = TeacherSalaryCalculations.objects.filter(teacher=teacher)
#             paid_qs       = TeacherSalaryPayments.objects.filter(teacher=teacher)
#             if month:
#                 calculated_qs = calculated_qs.filter(month=month)
#                 month_date    = datetime.strptime(month, '%Y-%m-%d')
#                 paid_qs       = paid_qs.filter(
#                     payment_date__year=month_date.year, payment_date__month=month_date.month
#                 )
#             calculated        = calculated_qs.aggregate(total=Sum('total_amount'))['total'] or 0
#             paid              = paid_qs.aggregate(total=Sum('amount'))['total'] or 0
#             total_calculated += calculated
#             total_paid       += paid
#             if calculated - paid > 0:
#                 debtors.append(teacher.full_name)
#
#         return Response({'total_calculated': total_calculated, 'total_paid': total_paid,
#                          'total_debt': total_calculated - total_paid,
#                          'debtors_count': len(debtors), 'month': month or 'Barchasi'})
#
#
# @extend_schema(tags=["Debts - Qarzdorlar"])
# class AllDebtsView(APIView):
#     def get(self, request):
#         month          = request.query_params.get('month')
#         student_debts  = Sale.objects.filter(debt_amount__gt=0)
#         if month:
#             student_debts = student_debts.filter(month=month)
#
#         student_total  = student_debts.aggregate(total=Sum('debt_amount'))['total'] or 0
#         student_count  = student_debts.count()
#         teachers       = Employee.objects.filter(position__icontains="o'qituvchi")
#         teacher_total_debt = teacher_debtors = 0
#
#         for teacher in teachers:
#             calculated_qs = TeacherSalaryCalculations.objects.filter(teacher=teacher)
#             paid_qs       = TeacherSalaryPayments.objects.filter(teacher=teacher)
#             if month:
#                 calculated_qs = calculated_qs.filter(month=month)
#                 month_date    = datetime.strptime(month, '%Y-%m-%d')
#                 paid_qs       = paid_qs.filter(
#                     payment_date__year=month_date.year, payment_date__month=month_date.month
#                 )
#             calculated = calculated_qs.aggregate(total=Sum('total_amount'))['total'] or 0
#             paid       = paid_qs.aggregate(total=Sum('amount'))['total'] or 0
#             debt       = calculated - paid
#             if debt > 0:
#                 teacher_total_debt += debt
#                 teacher_debtors    += 1
#
#         return Response({
#             'total_student_debt':   student_total,
#             'total_teacher_debt':   teacher_total_debt,
#             'total_debt':           student_total + teacher_total_debt,
#             'student_debtors_count': student_count,
#             'teacher_debtors_count': teacher_debtors,
#             'total_debtors_count':  student_count + teacher_debtors,
#             'month':                month or 'Barchasi',
#             'breakdown': {
#                 'students': {'debt': student_total,       'count': student_count},
#                 'teachers': {'debt': teacher_total_debt,  'count': teacher_debtors},
#             },
#         })
#
# # konversiya
#
#
# # ════════════════════════════════════════════════════════════════
# #  CONVERSION REPORT  (faqat o'qish — AuditLog shart emas)
# # ════════════════════════════════════════════════════════════════
#
# @extend_schema(tags=["CRM - Konversiya Hisobotlari"])
# class ConversionReportViewSet(viewsets.ViewSet):
#
#     @extend_schema(parameters=[
#         OpenApiParameter('start_date', str), OpenApiParameter('end_date', str),
#         OpenApiParameter('source', int),    OpenApiParameter('assigned_to', int),
#     ])
#     @action(detail=False, methods=['get'])
#     def overview(self, request):
#         start_date  = request.query_params.get('start_date')
#         end_date    = request.query_params.get('end_date')
#         source      = request.query_params.get('source')
#         assigned_to = request.query_params.get('assigned_to')
#
#         queryset = CRMLead.objects.all()
#         if start_date:
#             queryset = queryset.filter(created_at__gte=start_date)
#         if end_date:
#             queryset = queryset.filter(created_at__lte=end_date)
#         if source:
#             queryset = queryset.filter(source_id=source)
#         if assigned_to:
#             queryset = queryset.filter(assigned_to_id=assigned_to)
#
#         total     = queryset.count()
#         converted = queryset.filter(status='converted').count()
#
#         return Response({
#             'total_leads':      total,
#             'active_leads':     queryset.filter(status='active').count(),
#             'converted_leads':  converted,
#             'lost_leads':       queryset.filter(status='lost').count(),
#             'conversion_rate':  round((converted / total * 100) if total > 0 else 0, 2),
#             'date_range':       {'start': start_date, 'end': end_date},
#         })
#
#     @extend_schema(parameters=[OpenApiParameter('start_date', str), OpenApiParameter('end_date', str)])
#     @action(detail=False, methods=['get'])
#     def funnel(self, request):
#         start_date = request.query_params.get('start_date')
#         end_date   = request.query_params.get('end_date')
#         queryset   = CRMLead.objects.all()
#         if start_date:
#             queryset = queryset.filter(created_at__gte=start_date)
#         if end_date:
#             queryset = queryset.filter(created_at__lte=end_date)
#
#         total     = queryset.count()
#         pipelines = CRMPipelines.objects.all().order_by('position')
#         funnel    = []
#
#         for pipeline in pipelines:
#             count      = queryset.filter(pipline=pipeline).count()
#             percentage = round((count / total * 100) if total > 0 else 0, 2)
#
#             if pipeline.position > 1:
#                 prev = pipelines.filter(position=pipeline.position - 1).first()
#                 prev_count = queryset.filter(pipline=prev).count() if prev else 0
#                 conversion = round((count / prev_count * 100) if prev_count > 0 else 0, 2)
#             else:
#                 conversion = 100
#
#             funnel.append({
#                 'pipeline_name':     pipeline.name,
#                 'pipeline_position': pipeline.position,
#                 'total_leads':       count,
#                 'percentage':        percentage,
#                 'conversion_rate':   conversion,
#             })
#
#         return Response({'total_leads': total, 'funnel': funnel})
#
#     @action(detail=False, methods=['get'])
#     def by_source(self, request):
#         start_date = request.query_params.get('start_date')
#         end_date   = request.query_params.get('end_date')
#         queryset   = CRMLead.objects.all()
#         if start_date:
#             queryset = queryset.filter(created_at__gte=start_date)
#         if end_date:
#             queryset = queryset.filter(created_at__lte=end_date)
#
#         sources = queryset.values('source__name').annotate(
#             total=Count('id'),
#             active=Count('id', filter=Q(status='active')),
#             converted=Count('id', filter=Q(status='converted')),
#             lost=Count('id', filter=Q(status='lost')),
#         )
#
#         result = []
#         for s in sources:
#             total     = s['total']
#             converted = s['converted']
#             result.append({
#                 'source_name':    s['source__name'] or "Noma'lum",
#                 'total_leads':    total,
#                 'active':         s['active'],
#                 'converted':      converted,
#                 'lost':           s['lost'],
#                 'conversion_rate': round((converted / total * 100) if total > 0 else 0, 2),
#             })
#         result.sort(key=lambda x: x['conversion_rate'], reverse=True)
#         return Response(result)
#
#     @action(detail=False, methods=['get'])
#     def by_employee(self, request):
#         start_date = request.query_params.get('start_date')
#         end_date   = request.query_params.get('end_date')
#         queryset   = CRMLead.objects.all()
#         if start_date:
#             queryset = queryset.filter(created_at__gte=start_date)
#         if end_date:
#             queryset = queryset.filter(created_at__lte=end_date)
#
#         emp_data = queryset.values(
#             'assigned_to__first_name', 'assigned_to__last_name'
#         ).annotate(
#             total=Count('id'),
#             active=Count('id', filter=Q(status='active')),
#             converted=Count('id', filter=Q(status='converted')),
#             lost=Count('id', filter=Q(status='lost')),
#         )
#
#         result = []
#         for e in emp_data:
#             total     = e['total']
#             converted = e['converted']
#             full_name = f"{e['assigned_to__first_name'] or ''} {e['assigned_to__last_name'] or ''}".strip()
#             result.append({
#                 'employee_name':  full_name or 'Tayinlanmagan',
#                 'total_leads':    total,
#                 'active':         e['active'],
#                 'converted':      converted,
#                 'lost':           e['lost'],
#                 'conversion_rate': round((converted / total * 100) if total > 0 else 0, 2),
#             })
#         result.sort(key=lambda x: x['conversion_rate'], reverse=True)
#         return Response(result)
#
#     @action(detail=False, methods=['get'])
#     def pipeline_transitions(self, request):
#         start_date = request.query_params.get('start_date')
#         end_date   = request.query_params.get('end_date')
#         queryset   = CRMLeadsHistory.objects.select_related('old_pipeline', 'new_pipeline', 'lead', 'changed_by').all()
#         if start_date:
#             queryset = queryset.filter(changed_at__gte=start_date)
#         if end_date:
#             queryset = queryset.filter(changed_at__lte=end_date)
#
#         transitions = []
#         for h in queryset[:100]:
#             transitions.append({
#                 'lead_name':     h.lead.full_name,
#                 'from_pipeline': h.old_pipeline.name if h.old_pipeline else 'Yangi',
#                 'to_pipeline':   h.new_pipeline.name if h.new_pipeline else "Noma'lum",
#                 'changed_by':    h.changed_by.get_full_name() if h.changed_by else "Noma'lum",
#                 'changed_at':    h.changed_at,
#             })
#         return Response(transitions)
#
#     @action(detail=False, methods=['get'])
#     def lost_reasons(self, request):
#         start_date = request.query_params.get('start_date')
#         end_date   = request.query_params.get('end_date')
#         queryset   = CRMLeadLost.objects.select_related('reason', 'lead').all()
#         if start_date:
#             queryset = queryset.filter(created_at__gte=start_date)
#         if end_date:
#             queryset = queryset.filter(created_at__lte=end_date)
#
#         total       = queryset.count()
#         reasons     = queryset.values('reason__name').annotate(count=Count('id')).order_by('-count')
#         result      = [{
#             'reason':     r['reason__name'] or "Noma'lum",
#             'count':      r['count'],
#             'percentage': round((r['count'] / total * 100) if total > 0 else 0, 2),
#         } for r in reasons]
#         return Response({'total_lost': total, 'reasons': result})
#
#
# # ════════════════════════════════════════════════════════════════
# #  CRM LEAD (finance app ichida)
# # ════════════════════════════════════════════════════════════════
#
# @extend_schema(tags=["CRM - Leads"])
# class CRMLeadViewSet(viewsets.ModelViewSet):
#     queryset         = CRMLead.objects.select_related('source', 'pipline', 'assigned_to').all()
#     serializer_class = CRMLeadSerializer
#
#     def get_queryset(self):
#         queryset    = super().get_queryset()
#         status      = self.request.query_params.get('status')
#         source      = self.request.query_params.get('source')
#         pipeline    = self.request.query_params.get('pipeline')
#         assigned_to = self.request.query_params.get('assigned_to')
#         search      = self.request.query_params.get('search')
#
#         if status:
#             queryset = queryset.filter(status=status)
#         if source:
#             queryset = queryset.filter(source_id=source)
#         if pipeline:
#             queryset = queryset.filter(pipline_id=pipeline)
#         if assigned_to:
#             queryset = queryset.filter(assigned_to_id=assigned_to)
#         if search:
#             queryset = queryset.filter(
#                 Q(full_name__icontains=search) | Q(phone_number__icontains=search)
#             )
#         return queryset.order_by('-created_at')
#
#     def perform_create(self, serializer):
#         obj = serializer.save()
#         _log('lead', obj.id, 'create', None, {
#             'action':       'Lead yaratildi (finance)',
#             'full_name':    obj.full_name,
#             'phone_number': obj.phone_number,
#             'status':       obj.status,
#         }, self.request.user)
#
#     def perform_update(self, serializer):
#         old = {'status': serializer.instance.status,
#                'pipeline_id': str(serializer.instance.pipline_id) if serializer.instance.pipline_id else None}
#         obj = serializer.save()
#         _log('lead', obj.id, 'update', old, {
#             'status':      obj.status,
#             'pipeline_id': str(obj.pipline_id) if obj.pipline_id else None,
#         }, self.request.user)
#
#     def perform_destroy(self, instance):
#         _log('lead', instance.id, 'delete', {
#             'full_name': instance.full_name, 'status': instance.status,
#         }, None, self.request.user)
#         instance.delete()
#
#
# # ════════════════════════════════════════════════════════════════
# #  LEADS REPORT  (faqat o'qish)
# # ════════════════════════════════════════════════════════════════
#
# @extend_schema(tags=["Lidlar Hisoboti"])
# class LeadsReportViewSet(viewsets.ViewSet):
#
#     @extend_schema(parameters=[
#         OpenApiParameter('start_date', str, required=True),
#         OpenApiParameter('end_date', str, required=True),
#     ])
#     @action(detail=False, methods=['get'])
#     def statistics(self, request):
#         start_date = request.query_params.get('start_date')
#         end_date   = request.query_params.get('end_date')
#         if not start_date or not end_date:
#             return Response({'error': 'start_date va end_date majburiy'}, status=400)
#
#         leads       = CRMLead.objects.filter(created_at__date__gte=start_date, created_at__date__lte=end_date)
#         total_leads = leads.count()
#
#         by_source = leads.values('source__name').annotate(count=Count('id')).order_by('-count')
#         source_data = [{'source': i['source__name'] or 'Boshqalar', 'count': i['count'],
#                         'percentage': round((i['count'] / total_leads * 100) if total_leads > 0 else 0, 2)}
#                        for i in by_source]
#
#         by_month = leads.annotate(month=TruncMonth('created_at')).values('month').annotate(count=Count('id')).order_by('month')
#         month_data = [{'month': i['month'].strftime('%Y-%m'), 'month_name': i['month'].strftime('%B %Y'),
#                        'count': i['count']} for i in by_month]
#
#         return Response({'total_leads': total_leads, 'start_date': start_date, 'end_date': end_date,
#                          'summary': f"Lidlar soni: {total_leads} ({start_date} — {end_date})",
#                          'by_source': source_data, 'by_month': month_data})
#
#     @extend_schema(parameters=[OpenApiParameter('start_date', str, required=True), OpenApiParameter('end_date', str, required=True)])
#     @action(detail=False, methods=['get'])
#     def pie_chart(self, request):
#         start_date = request.query_params.get('start_date')
#         end_date   = request.query_params.get('end_date')
#         if not start_date or not end_date:
#             return Response({'error': 'start_date va end_date majburiy'}, status=400)
#
#         leads    = CRMLead.objects.filter(created_at__date__gte=start_date, created_at__date__lte=end_date)
#         total    = leads.count()
#         by_source = leads.values('source__name').annotate(count=Count('id')).order_by('-count')
#         result   = [{'label': i['source__name'] or 'Boshqalar', 'value': i['count'],
#                      'percentage': round((i['count'] / total * 100) if total > 0 else 0, 2)} for i in by_source]
#         return Response({'total': total, 'data': result})
#
#     @extend_schema(parameters=[OpenApiParameter('start_date', str, required=True), OpenApiParameter('end_date', str, required=True)])
#     @action(detail=False, methods=['get'])
#     def bar_chart(self, request):
#         start_date = request.query_params.get('start_date')
#         end_date   = request.query_params.get('end_date')
#         if not start_date or not end_date:
#             return Response({'error': 'start_date va end_date majburiy'}, status=400)
#
#         leads    = CRMLead.objects.filter(created_at__date__gte=start_date, created_at__date__lte=end_date)
#         by_month = leads.annotate(month=TruncMonth('created_at')).values('month').annotate(count=Count('id')).order_by('month')
#         result   = [{'month': i['month'].strftime('%Y-%m'), 'month_name': i['month'].strftime('%B %Y'),
#                      'count': i['count']} for i in by_month]
#         return Response({'data': result})
#
#     @action(detail=False, methods=['get'])
#     def summary(self, request):
#         end_date   = datetime.now().date()
#         start_date = end_date - timedelta(days=30)
#         prev_start = start_date - timedelta(days=30)
#
#         total      = CRMLead.objects.filter(created_at__date__gte=start_date, created_at__date__lte=end_date).count()
#         prev_total = CRMLead.objects.filter(created_at__date__gte=prev_start, created_at__date__lt=start_date).count()
#         top_source = CRMLead.objects.filter(created_at__date__gte=start_date, created_at__date__lte=end_date)\
#             .values('source__name').annotate(count=Count('id')).order_by('-count').first()
#         growth     = round(((total - prev_total) / prev_total * 100) if prev_total > 0 else 0, 2)
#
#         return Response({'period': 'Oxirgi 30 kun', 'total_leads': total,
#                          'top_source': top_source['source__name'] if top_source else "Noma'lum",
#                          'top_source_count': top_source['count'] if top_source else 0,
#                          'growth_percentage': growth, 'start_date': start_date, 'end_date': end_date})
#
#     @extend_schema(parameters=[
#         OpenApiParameter('start_date', str, required=True), OpenApiParameter('end_date', str, required=True),
#         OpenApiParameter('source', int),
#     ])
#     @action(detail=False, methods=['get'])
#     def detailed_report(self, request):
#         start_date = request.query_params.get('start_date')
#         end_date   = request.query_params.get('end_date')
#         source     = request.query_params.get('source')
#         if not start_date or not end_date:
#             return Response({'error': 'start_date va end_date majburiy'}, status=400)
#
#         leads = CRMLead.objects.filter(created_at__date__gte=start_date, created_at__date__lte=end_date)
#         if source:
#             leads = leads.filter(source_id=source)
#
#         total     = leads.count()
#         by_gender = leads.values('gender').annotate(count=Count('id'))
#         by_course = leads.exclude(expected_course='').values('expected_course').annotate(count=Count('id')).order_by('-count')[:5]
#
#         return Response({
#             'period': f"{start_date} — {end_date}",
#             'total_leads':      total,
#             'status_breakdown': {
#                 'active':    leads.filter(status='active').count(),
#                 'converted': leads.filter(status='converted').count(),
#                 'lost':      leads.filter(status='lost').count(),
#             },
#             'by_gender':   list(by_gender),
#             'top_courses': list(by_course),
#         })
#
#
# # ════════════════════════════════════════════════════════════════
# #  STUDENT LEAVES REPORT  (faqat o'qish)
# # ════════════════════════════════════════════════════════════════
#
# @extend_schema(tags=["Guruhni tark etgan o'quvchilar"])
# class StudentLeavesReportViewSet(viewsets.ViewSet):
#
#     @extend_schema(parameters=[
#         OpenApiParameter('start_date', str, required=True), OpenApiParameter('end_date', str, required=True),
#         OpenApiParameter('course', int), OpenApiParameter('teacher', int), OpenApiParameter('leave_reason', int),
#     ])
#     @action(detail=False, methods=['get'])
#     def statistics(self, request):
#         start_date   = request.query_params.get('start_date')
#         end_date     = request.query_params.get('end_date')
#         course       = request.query_params.get('course')
#         teacher      = request.query_params.get('teacher')
#         leave_reason = request.query_params.get('leave_reason')
#
#         if not start_date or not end_date:
#             return Response({'error': 'start_date va end_date majburiy'}, status=400)
#
#         leaves = StudentGroupLeaves.objects.filter(
#             leave_date__date__gte=start_date, leave_date__date__lte=end_date
#         ).select_related('student', 'group', 'leave_reason', 'created_by', 'group__course')
#
#         if course:
#             leaves = leaves.filter(group__course_id=course)
#         if teacher:
#             tg_ids = GroupTeacher.objects.filter(teacher_id=teacher).values_list('group_id', flat=True)
#             leaves = leaves.filter(group_id__in=tg_ids)
#         if leave_reason:
#             leaves = leaves.filter(leave_reason_id=leave_reason)
#
#         total_count = leaves.count()
#
#         # Ustoz kesimida
#         teacher_stats = {}
#         for tg in GroupTeacher.objects.filter(group_id__in=leaves.values_list('group_id', flat=True)).select_related('teacher', 'group'):
#             name = tg.teacher.user.full_name
#             cnt  = leaves.filter(group=tg.group).count()
#             teacher_stats[name] = teacher_stats.get(name, 0) + cnt
#
#         teacher_data = sorted([{'teacher': k, 'count': v} for k, v in teacher_stats.items()],
#                                key=lambda x: x['count'], reverse=True)
#
#         by_course = [{'course': i['group__course__name'] or "Noma'lum", 'count': i['count']}
#                      for i in leaves.values('group__course__name').annotate(count=Count('id')).order_by('-count')]
#
#         by_month = [{'month': i['month'].strftime('%Y-%m'), 'month_name': i['month'].strftime('%B %Y'),
#                      'count': i['count']}
#                     for i in leaves.annotate(month=TruncMonth('leave_date')).values('month').annotate(count=Count('id')).order_by('month')]
#
#         by_reason = [{'reason': i['leave_reason__name'] or "Noma'lum", 'count': i['count']}
#                      for i in leaves.values('leave_reason__name').annotate(count=Count('id')).order_by('-count')]
#
#         return Response({'total_count': total_count, 'period': f"{start_date} — {end_date}",
#                          'by_teacher': teacher_data, 'by_course': by_course,
#                          'by_month': by_month, 'by_reason': by_reason})
#
#     @extend_schema(parameters=[OpenApiParameter('start_date', str, required=True),
#                                 OpenApiParameter('end_date', str, required=True), OpenApiParameter('teacher', int)])
#     @action(detail=False, methods=['get'])
#     def by_teacher(self, request):
#         start_date = request.query_params.get('start_date')
#         end_date   = request.query_params.get('end_date')
#         teacher    = request.query_params.get('teacher')
#         if not start_date or not end_date:
#             return Response({'error': 'start_date va end_date majburiy'}, status=400)
#
#         leaves = StudentGroupLeaves.objects.filter(leave_date__date__gte=start_date, leave_date__date__lte=end_date)
#         tg_qs  = GroupTeacher.objects.select_related('teacher', 'group').filter(group_id__in=leaves.values_list('group_id', flat=True))
#         if teacher:
#             tg_qs = tg_qs.filter(teacher_id=teacher)
#
#         result = {}
#         for tg in tg_qs:
#             name = tg.teacher.user.full_name
#             result[name] = result.get(name, 0) + leaves.filter(group=tg.group).count()
#
#         data = sorted([{'teacher': k, 'count': v} for k, v in result.items()], key=lambda x: x['count'], reverse=True)
#         return Response({'data': data})
#
#     @extend_schema(parameters=[OpenApiParameter('start_date', str, required=True),
#                                 OpenApiParameter('end_date', str, required=True), OpenApiParameter('course', int)])
#     @action(detail=False, methods=['get'])
#     def by_course(self, request):
#         start_date = request.query_params.get('start_date')
#         end_date   = request.query_params.get('end_date')
#         course     = request.query_params.get('course')
#         if not start_date or not end_date:
#             return Response({'error': 'start_date va end_date majburiy'}, status=400)
#
#         leaves = StudentGroupLeaves.objects.filter(leave_date__date__gte=start_date, leave_date__date__lte=end_date)
#         if course:
#             leaves = leaves.filter(group__course_id=course)
#         data = [{'course': i['group__course__name'] or "Noma'lum", 'count': i['count']}
#                 for i in leaves.values('group__course__name').annotate(count=Count('id')).order_by('-count')]
#         return Response({'data': data})
#
#     @extend_schema(parameters=[OpenApiParameter('start_date', str, required=True), OpenApiParameter('end_date', str, required=True)])
#     @action(detail=False, methods=['get'])
#     def by_month(self, request):
#         start_date = request.query_params.get('start_date')
#         end_date   = request.query_params.get('end_date')
#         if not start_date or not end_date:
#             return Response({'error': 'start_date va end_date majburiy'}, status=400)
#
#         leaves = StudentGroupLeaves.objects.filter(leave_date__date__gte=start_date, leave_date__date__lte=end_date)
#         data   = [{'month': i['month'].strftime('%Y-%m'), 'month_name': i['month'].strftime('%B %Y'), 'count': i['count']}
#                   for i in leaves.annotate(month=TruncMonth('leave_date')).values('month').annotate(count=Count('id')).order_by('month')]
#         return Response({'data': data})
#
#     @extend_schema(parameters=[OpenApiParameter('start_date', str, required=True),
#                                 OpenApiParameter('end_date', str, required=True), OpenApiParameter('leave_reason', int)])
#     @action(detail=False, methods=['get'])
#     def by_reason(self, request):
#         start_date   = request.query_params.get('start_date')
#         end_date     = request.query_params.get('end_date')
#         leave_reason = request.query_params.get('leave_reason')
#         if not start_date or not end_date:
#             return Response({'error': 'start_date va end_date majburiy'}, status=400)
#
#         leaves = StudentGroupLeaves.objects.filter(leave_date__date__gte=start_date, leave_date__date__lte=end_date)
#         if leave_reason:
#             leaves = leaves.filter(leave_reason_id=leave_reason)
#         data = [{'reason': i['leave_reason__name'] or "Noma'lum", 'count': i['count']}
#                 for i in leaves.values('leave_reason__name').annotate(count=Count('id')).order_by('-count')]
#         return Response({'data': data})
#
#     @action(detail=False, methods=['get'])
#     def detailed_list(self, request):
#         start_date   = request.query_params.get('start_date')
#         end_date     = request.query_params.get('end_date')
#         course       = request.query_params.get('course')
#         teacher      = request.query_params.get('teacher')
#         leave_reason = request.query_params.get('leave_reason')
#         if not start_date or not end_date:
#             return Response({'error': 'start_date va end_date majburiy'}, status=400)
#
#         leaves = StudentGroupLeaves.objects.filter(
#             leave_date__date__gte=start_date, leave_date__date__lte=end_date
#         ).select_related('student', 'group', 'leave_reason', 'created_by', 'group__course')
#
#         if course:
#             leaves = leaves.filter(group__course_id=course)
#         if teacher:
#             tg_ids = GroupTeacher.objects.filter(teacher_id=teacher).values_list('group_id', flat=True)
#             leaves = leaves.filter(group_id__in=tg_ids)
#         if leave_reason:
#             leaves = leaves.filter(leave_reason_id=leave_reason)
#
#         return Response(StudentGroupLeavesSerializer(leaves, many=True).data)
#
#
# # ════════════════════════════════════════════════════════════════
# #  STUDENT GROUP LEAVES VIEWSET
# # ════════════════════════════════════════════════════════════════
#
# @extend_schema(tags=["StudentGroupLeaves"])
# class StudentGroupLeavesViewSet(viewsets.ModelViewSet):
#     queryset         = StudentGroupLeaves.objects.select_related('student', 'group', 'leave_reason', 'created_by').all()
#     serializer_class = StudentGroupLeavesSerializer
#
#     def get_queryset(self):
#         queryset   = super().get_queryset()
#         student    = self.request.query_params.get('student')
#         group      = self.request.query_params.get('group')
#         start_date = self.request.query_params.get('start_date')
#         end_date   = self.request.query_params.get('end_date')
#
#         if student:
#             queryset = queryset.filter(student_id=student)
#         if group:
#             queryset = queryset.filter(group_id=group)
#         if start_date:
#             queryset = queryset.filter(leave_date__gte=start_date)
#         if end_date:
#             queryset = queryset.filter(leave_date__lte=end_date)
#         return queryset.order_by('-leave_date')
#
#     def perform_create(self, serializer):
#         obj = serializer.save()
#         _log('student', obj.student_id, 'update', None, {
#             'action':     'Guruhdan chiqarildi (StudentGroupLeavesViewSet)',
#             'group_id':   str(obj.group_id),
#             'leave_date': str(obj.leave_date),
#             'reason_id':  str(obj.leave_reason_id) if obj.leave_reason_id else None,
#         }, self.request.user)
#
#     def perform_destroy(self, instance):
#         _log('student', instance.student_id, 'update',
#              {'group_id': str(instance.group_id), 'leave_date': str(instance.leave_date)},
#              {'action': 'StudentGroupLeaves yozuvi o\'chirildi'},
#              self.request.user)
#         instance.delete()
#
#
# # ════════════════════════════════════════════════════════════════
# #  LEAVE REASON
# # ════════════════════════════════════════════════════════════════
#
# @extend_schema(tags=["LeaveReason"])
# class LeaveReasonViewSet(viewsets.ModelViewSet):
#     queryset         = LeaveReason.objects.all()
#     serializer_class = LeaveReasonSerializer
#
#     def get_queryset(self):
#         queryset  = super().get_queryset()
#         is_active = self.request.query_params.get('is_active')
#         if is_active:
#             queryset = queryset.filter(is_active=is_active == 'true')
#         return queryset
#
#     def perform_create(self, serializer):
#         obj = serializer.save()
#         _log('other', obj.id, 'create', None, {'action': 'Ketish sababi yaratildi', 'name': obj.name}, self.request.user)
#
#     def perform_update(self, serializer):
#         old = {'name': serializer.instance.name, 'is_active': serializer.instance.is_active}
#         obj = serializer.save()
#         _log('other', obj.id, 'update', old, {'name': obj.name, 'is_active': obj.is_active}, self.request.user)
#
#     def perform_destroy(self, instance):
#         _log('other', instance.id, 'delete', {'name': instance.name}, None, self.request.user)
#         instance.delete()
#
# # ════════════════════════════════════════════════════════════════
# #  ALL PAYMENTS  (faqat o'qish)
# # ════════════════════════════════════════════════════════════════
#
# class AllPaymentsAPIView(APIView):
#     """Barcha to'lovlar sahifasi"""
#     permission_classes = [IsAuthenticated]
#
#     def get(self, request):
#         date_from    = request.GET.get('date_from')
#         date_to      = request.GET.get('date_to')
#         queryset     = Payment.objects.all()
#
#         if date_from:
#             queryset = queryset.filter(created_at__date__gte=date_from)
#         if date_to:
#             queryset = queryset.filter(created_at__date__lte=date_to)
#
#         total_payments = queryset.aggregate(total=Sum('salary'))['total'] or 0
#
#         expenses_qs = Expenses.objects.all()
#         if date_from:
#             expenses_qs = expenses_qs.filter(expense_date__date__gte=date_from)
#         if date_to:
#             expenses_qs = expenses_qs.filter(expense_date__date__lte=date_to)
#
#         total_expenses = expenses_qs.aggregate(total=Sum('amount'))['total'] or 0
#         total_profit   = total_payments - total_expenses
#
#         chart_qs = queryset.annotate(day=TruncDate('created_at')).values('day').annotate(
#             daily_sum=Sum('salary')
#         ).order_by('day')
#
#         labels     = [i['day'].strftime('%Y-%m-%d') for i in chart_qs]
#         values     = [float(i['daily_sum'] or 0) for i in chart_qs]
#         cumulative = []
#         running    = 0
#         for v in values:
#             running += v
#             cumulative.append(running)
#
#         page      = int(request.GET.get('page', 1))
#         page_size = int(request.GET.get('page_size', 20))
#         start     = (page - 1) * page_size
#         paginated = queryset[start: start + page_size]
#
#         from .serializers import PaymentListSerializer
#         return Response({
#             'success':        True,
#             'count':          queryset.count(),
#             'total_payments': float(total_payments),
#             'total_profit':   float(total_profit),
#             'period':         {'from': date_from, 'to': date_to},
#             'chart':          {'labels': labels, 'values': values, 'cumulative': cumulative},
#             'results':        PaymentListSerializer(paginated, many=True).data,
#         })
#
#
# # ════════════════════════════════════════════════════════════════
# #  WITHDRAWALS  (faqat o'qish)
# # ════════════════════════════════════════════════════════════════
#
# class WithdrawalsAPIView(APIView):
#     """Yechib olish sahifasi"""
#     permission_classes = [IsAuthenticated]
#
#     def get(self, request):
#         queryset = DetailedExpense.objects.all().select_related('subcategory', 'payment_type')
#         filters  = Q()
#
#         if date_from := request.GET.get('date_from'):
#             filters &= Q(date__date__gte=date_from)
#         if date_to := request.GET.get('date_to'):
#             filters &= Q(date__date__lte=date_to)
#         if search := request.GET.get('search'):
#             filters &= Q(name__icontains=search) | Q(comment__icontains=search)
#         if min_sum := request.GET.get('min_sum'):
#             filters &= Q(amount__gte=min_sum)
#         if max_sum := request.GET.get('max_sum'):
#             filters &= Q(amount__lte=max_sum)
#
#         queryset           = queryset.filter(filters).order_by(request.GET.get('ordering', '-date'))
#         total_withdrawals  = queryset.aggregate(total=Sum('amount'))['total'] or 0
#
#         chart_qs = queryset.annotate(day=TruncDate('date')).values('day').annotate(daily_sum=Sum('amount')).order_by('day')
#         labels   = [i['day'].strftime('%Y-%m-%d') for i in chart_qs]
#         values   = [float(i['daily_sum'] or 0) for i in chart_qs]
#
#         page      = int(request.GET.get('page', 1))
#         page_size = int(request.GET.get('page_size', 20))
#         start     = (page - 1) * page_size
#         paginated = queryset[start: start + page_size]
#
#         return Response({
#             'success':           True,
#             'total_withdrawals': float(total_withdrawals),
#             'period':            {'from': request.GET.get('date_from'), 'to': request.GET.get('date_to')},
#             'chart':             {'labels': labels, 'values': values},
#             'results':           WithdrawalListSerializer(paginated, many=True).data,
#         })
#
#
# # ════════════════════════════════════════════════════════════════
# #  EXPENSES API VIEW
# # ════════════════════════════════════════════════════════════════
#
# class ExpensesAPIView(APIView):
#     """Xarajatlar sahifasi"""
#     permission_classes = [IsAuthenticated]
#
#     def get(self, request):
#         from .serializers import ExpenseListSerializer
#         queryset = DetailedExpense.objects.all().select_related('subcategory', 'payment_type')
#
#         if date_from := request.GET.get('date_from'):
#             queryset = queryset.filter(date__date__gte=date_from)
#         if date_to := request.GET.get('date_to'):
#             queryset = queryset.filter(date__date__lte=date_to)
#         if search := request.GET.get('search'):
#             queryset = queryset.filter(Q(name__icontains=search) | Q(comment__icontains=search))
#         if subcategory_id := request.GET.get('subcategory'):
#             queryset = queryset.filter(subcategory_id=subcategory_id)
#         if payment_type := request.GET.get('payment_type'):
#             queryset = queryset.filter(payment_type__name=payment_type)
#         if min_sum := request.GET.get('min_sum'):
#             queryset = queryset.filter(amount__gte=min_sum)
#         if max_sum := request.GET.get('max_sum'):
#             queryset = queryset.filter(amount__lte=max_sum)
#
#         queryset       = queryset.order_by('-date')
#         total_expenses = queryset.aggregate(total=Sum('amount'))['total'] or 0
#
#         chart_qs      = queryset.annotate(day=TruncDate('date')).values('day').annotate(daily_sum=Sum('amount')).order_by('day')
#         chart_labels  = [i['day'].strftime('%Y-%m-%d') for i in chart_qs]
#         chart_values  = [float(i['daily_sum'] or 0) for i in chart_qs]
#         by_subcategory = queryset.values('subcategory__name').annotate(total=Sum('amount')).order_by('-total')
#
#         page      = int(request.GET.get('page', 1))
#         page_size = int(request.GET.get('page_size', 20))
#         start     = (page - 1) * page_size
#         paginated = queryset[start: start + page_size]
#
#         return Response({'success': True, 'total_expenses': float(total_expenses),
#                          'chart': {'labels': chart_labels, 'values': chart_values},
#                          'by_subcategory': list(by_subcategory),
#                          'results': ExpenseListSerializer(paginated, many=True).data})
#
#     def post(self, request):
#         from .serializers import ExpenseListSerializer, ExpenseCreateUpdateSerializer
#         serializer = ExpenseCreateUpdateSerializer(data=request.data)
#         if serializer.is_valid():
#             expense = serializer.save()
#
#             # ── AuditLog ──
#             _log('other', expense.id, 'create', None, {
#                 'action': 'Xarajat qo\'shildi (ExpensesAPIView)',
#                 'amount': str(expense.amount),
#                 'date':   str(expense.date),
#             }, request.user)
#
#             return Response(ExpenseListSerializer(expense).data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#
# class ExpenseDetailAPIView(APIView):
#     permission_classes = [IsAuthenticated]
#
#     def get_object(self, pk):
#         try:
#             return DetailedExpense.objects.get(pk=pk)
#         except DetailedExpense.DoesNotExist:
#             return None
#
#     def patch(self, request, pk):
#         from .serializers import ExpenseListSerializer, ExpenseCreateUpdateSerializer
#         expense = self.get_object(pk)
#         if not expense:
#             return Response({'error': 'Topilmadi'}, status=404)
#
#         old_amount = str(expense.amount)
#         serializer = ExpenseCreateUpdateSerializer(expense, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#
#             _log('other', expense.id, 'update', {'amount': old_amount}, {
#                 'amount': str(expense.amount), 'comment': expense.comment,
#             }, request.user)
#
#             return Response(ExpenseListSerializer(expense).data)
#         return Response(serializer.errors, status=400)
#
#     def delete(self, request, pk):
#         expense = self.get_object(pk)
#         if not expense:
#             return Response({'error': 'Topilmadi'}, status=404)
#
#         _log('other', expense.id, 'delete', {'amount': str(expense.amount), 'date': str(expense.date)},
#              None, request.user)
#
#         expense.delete()
#         return Response({'success': True, 'message': "O'chirildi"})
#
#
# class ExpenseCategoryAPIView(APIView):
#     permission_classes = [IsAuthenticated]
#
#     def get(self, request):
#         from .serializers import ExpenseCategorySerializer
#         categories = ExpenseCategory.objects.all()
#         return Response(ExpenseCategorySerializer(categories, many=True).data)
#
#     def post(self, request):
#         from .serializers import ExpenseCategorySerializer
#         serializer = ExpenseCategorySerializer(data=request.data)
#         if serializer.is_valid():
#             category = serializer.save()
#
#             _log('other', category.id, 'create', None, {
#                 'action': 'Xarajat kategoriyasi yaratildi', 'name': category.name,
#             }, request.user)
#
#             return Response(serializer.data, status=201)
#         return Response(serializer.errors, status=400)
#
#
# class ExpenseCategoryDetailAPIView(APIView):
#     permission_classes = [IsAuthenticated]
#
#     def get_object(self, pk):
#         try:
#             return ExpenseCategory.objects.get(pk=pk)
#         except ExpenseCategory.DoesNotExist:
#             return None
#
#     def patch(self, request, pk):
#         from .serializers import ExpenseCategorySerializer
#         category = self.get_object(pk)
#         if not category:
#             return Response({'error': 'Topilmadi'}, status=404)
#
#         old_name   = category.name
#         serializer = ExpenseCategorySerializer(category, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             _log('other', category.id, 'update', {'name': old_name}, {'name': category.name}, request.user)
#             return Response(serializer.data)
#         return Response(serializer.errors, status=400)
#
#     def delete(self, request, pk):
#         category = self.get_object(pk)
#         if not category:
#             return Response({'error': 'Topilmadi'}, status=404)
#         _log('other', category.id, 'delete', {'name': category.name}, None, request.user)
#         category.delete()
#         return Response({'success': True, 'message': "O'chirildi"})
#
#
# # ════════════════════════════════════════════════════════════════
# #  TEACHER SALARY RULES API VIEW
# # ════════════════════════════════════════════════════════════════
#
# class TeacherSalaryRulesAPIView(APIView):
#     permission_classes = [IsAuthenticated]
#
#     def get(self, request):
#         from .serializers import TeacherSalaryRuleSerializer
#         queryset = TeacherSalaryRules.objects.select_related('teacher').all()
#         teacher  = request.GET.get('teacher')
#         group    = request.GET.get('group')
#         month    = request.GET.get('month')
#
#         if teacher:
#             queryset = queryset.filter(teacher_id=teacher)
#         if group:
#             queryset = queryset.filter(group_id=group)
#         if month:
#             queryset = queryset.filter(effective_from__lte=month, effective_to__gte=month)
#
#         return Response({'success': True, 'count': queryset.count(),
#                          'results': TeacherSalaryRuleSerializer(queryset, many=True).data})
#
#     def post(self, request):
#         from .serializers import TeacherSalaryRuleSerializer, TeacherSalaryRuleCreateSerializer
#         serializer = TeacherSalaryRuleCreateSerializer(data=request.data)
#         if serializer.is_valid():
#             rule = serializer.save()
#
#             _log('other', rule.id, 'create', None, {
#                 'action':              "O'qituvchi maosh qoidasi yaratildi (TeacherSalaryRulesAPIView)",
#                 'teacher_id':          str(rule.teacher_id),
#                 'percent_per_student': str(rule.percent_per_student),
#                 'fixed_bonus':         str(rule.fixed_bonus),
#             }, request.user)
#
#             return Response(TeacherSalaryRuleSerializer(rule).data, status=201)
#         return Response(serializer.errors, status=400)
#
#
# class TeacherSalaryRuleDetailAPIView(APIView):
#     permission_classes = [IsAuthenticated]
#
#     def get_object(self, pk):
#         try:
#             return TeacherSalaryRules.objects.get(pk=pk)
#         except TeacherSalaryRules.DoesNotExist:
#             return None
#
#     def patch(self, request, pk):
#         from .serializers import TeacherSalaryRuleSerializer, TeacherSalaryRuleCreateSerializer
#         rule = self.get_object(pk)
#         if not rule:
#             return Response({'error': 'Topilmadi'}, status=404)
#
#         old = {'percent_per_student': str(rule.percent_per_student), 'fixed_bonus': str(rule.fixed_bonus)}
#         serializer = TeacherSalaryRuleCreateSerializer(rule, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             _log('other', rule.id, 'update', old, {
#                 'percent_per_student': str(rule.percent_per_student), 'fixed_bonus': str(rule.fixed_bonus),
#             }, request.user)
#             return Response(TeacherSalaryRuleSerializer(rule).data)
#         return Response(serializer.errors, status=400)
#
#     def delete(self, request, pk):
#         rule = self.get_object(pk)
#         if not rule:
#             return Response({'error': 'Topilmadi'}, status=404)
#         _log('other', rule.id, 'delete', {'teacher_id': str(rule.teacher_id)}, None, request.user)
#         rule.delete()
#         return Response({'success': True, 'message': "O'chirildi"})
#
#
# class TeacherSalaryCalculateAPIView(APIView):
#     permission_classes = [IsAuthenticated]
#
#     def post(self, request):
#         from .serializers import TeacherSalaryCalculationSerializer
#         month_str = request.data.get('month')
#         if not month_str:
#             return Response({'error': 'month majburiy (YYYY-MM)'}, status=400)
#
#         try:
#             from datetime import datetime as dt
#             month_date = dt.strptime(month_str, '%Y-%m').date()
#         except ValueError:
#             return Response({'error': "Noto'g'ri sana formati (YYYY-MM)"}, status=400)
#
#         rules         = TeacherSalaryRules.objects.filter(
#             effective_from__lte=month_date, effective_to__gte=month_date
#         ).select_related('teacher')
#
#         calculations  = []
#         total_amount  = 0
#
#         for rule in rules:
#             student_count = 0
#             amount = (student_count * rule.percent_per_student) + rule.fixed_bonus
#
#             calc, created = TeacherSalaryCalculations.objects.update_or_create(
#                 teacher=rule.teacher, month=month_str,
#                 defaults={
#                     'student_count': student_count, 'percent': rule.percent_per_student,
#                     'total_amount': amount, 'calculated_at': timezone.now().date(),
#                 }
#             )
#
#             _log('other', calc.id, 'create' if created else 'update', None, {
#                 'action':       'TeacherSalaryCalculateAPIView - maosh hisoblandi',
#                 'teacher_id':   str(rule.teacher_id),
#                 'total_amount': str(amount),
#                 'month':        month_str,
#             }, request.user)
#
#             calculations.append(TeacherSalaryCalculationSerializer(calc).data)
#             total_amount += amount
#
#         return Response({'success': True, 'month': month_str,
#                          'total_amount': float(total_amount),
#                          'teacher_count': rules.count(), 'calculations': calculations})
#
#
# # ════════════════════════════════════════════════════════════════
# #  DEBTORS  (faqat o'qish)
# # ════════════════════════════════════════════════════════════════
#
# class DebtorsAPIView(APIView):
#     """Qarzdorlar sahifasi"""
#     permission_classes = [IsAuthenticated]
#
#     def get(self, request):
#         from academics.models import Student, StudentGroup, StudentBalances
#
#         queryset = Student.objects.filter(
#             Sbalances_student__balance__lt=0
#         ).prefetch_related('Sbalances_student', 'sgroup_student__group')
#
#         if search := request.GET.get('search'):
#             queryset = queryset.filter(
#                 Q(full_name__icontains=search) | Q(phone_number__icontains=search)
#             )
#         if group_id := request.GET.get('group'):
#             queryset = queryset.filter(sgroup_student__group_id=group_id)
#         if min_balance := request.GET.get('min_balance'):
#             queryset = queryset.filter(Sbalances_student__balance__gte=min_balance)
#         if max_balance := request.GET.get('max_balance'):
#             queryset = queryset.filter(Sbalances_student__balance__lte=max_balance)
#
#         queryset = queryset.order_by(request.GET.get('ordering', '-Sbalances_student__balance'))
#
#         total_debt = abs(StudentBalances.objects.filter(balance__lt=0).aggregate(total=Sum('balance'))['total'] or 0)
#
#         page      = int(request.GET.get('page', 1))
#         page_size = int(request.GET.get('page_size', 20))
#         start     = (page - 1) * page_size
#         paginated = queryset[start: start + page_size]
#
#         results = []
#         for student in paginated:
#             balance_obj = student.Sbalances_student.first()
#             bal         = float(balance_obj.balance) if balance_obj else 0
#             sg          = student.sgroup_student.first()
#
#             results.append({
#                 'id':          student.id,
#                 'ism':         student.full_name,
#                 'telefon':     student.phone_number,
#                 'balans':      bal,
#                 'guruh':       sg.group.name if sg else None,
#                 'sana':        student.created_at.strftime('%d.%m.%Y %H:%M'),
#                 'holati':      'active' if bal >= 0 else 'inactive',
#                 'holati_rangi': 'green' if bal >= 0 else 'red',
#             })
#
#         return Response({
#             'success':            True,
#             'total_debt':         float(total_debt),
#             'period_total_debt':  float(total_debt),
#             'count':              queryset.count(),
#             'results':            results,
#         })