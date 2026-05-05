from datetime import timezone
from .models import ExpenseCategory, MonthlyIncome,CallLog
from django.db.models import Sum
from .models import Bonus, Fine, Salary
from academics.models.teacher import TeacherSalaryRules, TeacherSalaryPayments, TeacherSalaryCalculations
from crm.models import (CRMSource, CRMLead, CRMActivity)
from academics.models.student import (StudentGroupLeaves,
                                      LeaveReason)
from .models import ExpenseSubcategory
# finance/serializers.py
from rest_framework import serializers
from .models import Payment, Sale, DetailedExpense, Expenses  # o'zingizning modellaringizni qo'ying

 # guruh modeli

class ExpenseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseCategory
        fields = '__all__'


class ExpensesSerializer(serializers.ModelSerializer):
    # Modelda bor maydonlar asosida nomlarni (name) chiqarish
    category_name = serializers.CharField(source='category.name', read_only=True, default="Boshqa")
    branch_name = serializers.CharField(source='branch.name', read_only=True, default="-")

    class Meta:
        model = Expenses
        # Modelga yangi qo'shilgan name, recipient, payment_type larni ham kiritamiz
        fields = [
            'id',
            'category',
            'category_name', # Rasmda: Turkum
            'name',          # Rasmda: Nomi (yangi qo'shildi)
            'amount',        # Rasmda: Sum
            'expense_date',  # Rasmda: Sana
            'recipient',     # Rasmda: Oluvchi (yangi qo'shildi)
            'payment_type',  # To'lov turi (cash/card)
            'comment',       # Rasmda: Izoh
            'branch_name',
            'created_at'
        ]


class MonthlyIncomeSerializer(serializers.ModelSerializer):
    net_profit = serializers.SerializerMethodField()

    class Meta:
        model = MonthlyIncome
        fields = '__all__'

    def get_net_profit(self, obj):
        month_expenses = Expenses.objects.filter(
            expense_date__year=obj.month.year,
            expense_date__month=obj.month.month
        ).aggregate(total=Sum('amount'))['total'] or 0
        return obj.total_amount - month_expenses


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'


class SaleSerializer(serializers.ModelSerializer):
    paid_amount = serializers.SerializerMethodField()

    class Meta:
        model = Sale
        fields = '__all__'

    def get_paid_amount(self, obj):
        return obj.amount - obj.debt_amount

    def validate_amount(self, value):
        if value > 500000:
            raise serializers.ValidationError("Summa 500,000 so'mdan oshmasligi kerak")
        return value


class ExpenseSubcategorySerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    total_expenses = serializers.SerializerMethodField()

    class Meta:
        model = ExpenseSubcategory
        fields = '__all__'

    def get_total_expenses(self, obj):
        return obj.detailed_expenses.aggregate(total=Sum('amount'))['total'] or 0


class DetailedExpenseSerializer(serializers.ModelSerializer):
    subcategory_name = serializers.CharField(source='subcategory.name', read_only=True)
    payment_name = serializers.CharField(source='payment_type.name', read_only=True)

    class Meta:
        model = DetailedExpense
        fields = '__all__'

    def validate_amount(self, value):
        if value and value > 1000000:
            raise serializers.ValidationError("Summa 1,000,000 so'mdan oshmasligi kerak")
        return value

class BonusSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)

    class Meta:
        model = Bonus
        fields = '__all__'


class FineSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)

    class Meta:
        model = Fine
        fields = '__all__'


class SalarySerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    payment_name = serializers.CharField(source='payment_type.name', read_only=True)

    class Meta:
        model = Salary
        fields = '__all__'
        read_only_fields = ('total_amount',)

class TeacherSalaryRulesSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.full_name', read_only=True)

    class Meta:
        model = TeacherSalaryRules
        fields = '__all__'

    def validate(self, data):
        if data.get('effective_from') and data.get('effective_to'):
            if data['effective_from'] > data['effective_to']:
                raise serializers.ValidationError("effective_from effective_to dan katta bo'lmasligi kerak")
        return data


class TeacherSalaryPaymentsSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.full_name', read_only=True)

    class Meta:
        model = TeacherSalaryPayments
        fields = '__all__'


class TeacherSalaryCalculationsSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.full_name', read_only=True)
    group_name = serializers.CharField(source='group.name', read_only=True)

    class Meta:
        model = TeacherSalaryCalculations
        fields = '__all__'
        read_only_fields = ('total_amount',)

# bu sanan boyicha ish haqi
class PayPeriodSerializer(serializers.Serializer):
    """Sana tanlash uchun serializer"""
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    name = serializers.CharField(max_length=100, required=False)

    def validate(self, data):
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError("Boshlanish sanasi tugash sanasidan katta bo'lmasligi kerak")
        return data


class BulkSalaryConfigSerializer(serializers.Serializer):
    """Barcha ustozlar uchun sozlamalar"""
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    percent_per_student = serializers.DecimalField(max_digits=12, decimal_places=2)
    fixed_bonus = serializers.DecimalField(max_digits=12, decimal_places=2)
    apply_to_all = serializers.BooleanField(default=True)
# qarzdorlar
class StudentDebtSerializer(serializers.Serializer):
    """Talaba qarzi"""
    id = serializers.IntegerField()
    customer_name = serializers.CharField()
    phone = serializers.CharField()
    course = serializers.CharField()
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    debt_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    paid_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    sale_date = serializers.DateTimeField()
    month = serializers.DateField()

class TeacherDebtSerializer(serializers.Serializer):
    """Ustoz qarzi"""
    teacher_id = serializers.IntegerField()
    teacher_name = serializers.CharField()
    phone = serializers.CharField()
    calculated_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    paid_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    debt_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    month = serializers.CharField()

class AllDebtsSerializer(serializers.Serializer):
    """Umumiy qarzlar"""
    total_student_debt = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_teacher_debt = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_debt = serializers.DecimalField(max_digits=12, decimal_places=2)
    student_debtors_count = serializers.IntegerField()
    teacher_debtors_count = serializers.IntegerField()
    total_debtors_count = serializers.IntegerField()

# konversiya

class CRMSourceSerializer(serializers.ModelSerializer):
    leads_count = serializers.SerializerMethodField()

    class Meta:
        model = CRMSource
        fields = '__all__'

    def get_leads_count(self, obj):
        return obj.source.count()


# class CRMPipelinesSerializer(serializers.ModelSerializer):
#     leads_count = serializers.SerializerMethodField()
#
#     class Meta:
#         model = CRMPipelines
#         fields = '__all__'
#
#     def get_leads_count(self, obj):
#         return obj.pipline.count()
#

class CRMLeadSerializer(serializers.ModelSerializer):
    source_name = serializers.CharField(source='source.name', read_only=True)
    pipeline_name = serializers.CharField(source='pipline.name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)

    class Meta:
        model = CRMLead
        fields = '__all__'


class CRMActivitySerializer(serializers.ModelSerializer):
    lead_name = serializers.CharField(source='lead.full_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = CRMActivity
        fields = '__all__'


class ConversionFunnelSerializer(serializers.Serializer):
    """Sotuv voronkasi ma'lumotlari"""
    pipeline_name = serializers.CharField()
    pipeline_position = serializers.IntegerField()
    total_leads = serializers.IntegerField()
    percentage = serializers.DecimalField(max_digits=5, decimal_places=2)
    conversion_rate = serializers.DecimalField(max_digits=5, decimal_places=2)

# Lid hisobotlarini ko'rish uchun API chqiaris
class LeadsReportSerializer(serializers.Serializer):
    start_date = serializers.DateField()
    end_date = serializers.DateField()

    def validate(self, data):
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError("Boshlanish sanasi tugash sanasidan katta bo'lmasligi kerak")
        return data


class LeadsStatisticsSerializer(serializers.Serializer):
    total_leads = serializers.IntegerField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    by_source = serializers.ListField()
    by_month = serializers.ListField()



# Guruhni tark etgan talabalar hisoboti ko'rish uchun API yaratish

class LeaveReasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveReason
        fields = '__all__'


class StudentGroupLeavesSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    group_name = serializers.CharField(source='group.name', read_only=True)
    course_name = serializers.CharField(source='group.course.name', read_only=True)
    reason_name = serializers.CharField(source='leave_reason.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)

    class Meta:
        model = StudentGroupLeaves
        fields = '__all__'


class StudentLeavesReportSerializer(serializers.Serializer):
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    course = serializers.IntegerField(required=False)
    teacher = serializers.IntegerField(required=False)
    leave_reason = serializers.IntegerField(required=False)

    def validate(self, data):
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError("Boshlanish sanasi tugash sanasidan katta bo'lmasligi kerak")
        return data


class WorklyConnectionTestSerializer(serializers.Serializer):
    """Ulanishni tekshirish uchun"""
    client_id = serializers.CharField()
    client_secret = serializers.CharField()
    username = serializers.CharField()
    password = serializers.CharField()


class CallLogSerializer(serializers.ModelSerializer):
    caller_full_name = serializers.CharField(source='caller.full_name', read_only=True)
    audio_url = serializers.SerializerMethodField()
    duration_formatted = serializers.SerializerMethodField()

    class Meta:
        model = CallLog
        fields = '__all__'

    def get_audio_url(self, obj):
        if obj.audio_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.audio_file.url)
            return obj.audio_file.url
        return None

    def get_duration_formatted(self, obj):
        """Davomiyatni formatlash (MM:SS)"""
        minutes = obj.duration // 60
        seconds = obj.duration % 60
        return f"{minutes:02d}:{seconds:02d}"


class CallLogFilterSerializer(serializers.Serializer):
    """Filtrlash parametrlari"""
    date = serializers.DateField(required=False)
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    call_type = serializers.ChoiceField(
        choices=['all', 'incoming', 'outgoing', 'missed', 'answered_connected',
                 'unanswered_not_connected', 'no_answer'],
        required=False
    )



class PaymentListSerializer(serializers.ModelSerializer):
    """Jadvalda ko'rsatiladigan to'lovlar uchun"""
    student_name = serializers.CharField(source='student.full_name', read_only=True, allow_null=True)
    student_phone = serializers.CharField(source='student.phone_number', read_only=True, allow_null=True)
    group_name = serializers.SerializerMethodField()
    course_name = serializers.SerializerMethodField()
    teacher_name = serializers.SerializerMethodField()
    employee_name = serializers.CharField(source='accepted_by.full_name', read_only=True, allow_null=True)
    date = serializers.DateField(source='transaction_date', read_only=True)  # agar transaction_date bo'lsa

    class Meta:
        model = Payment  # agar to'lovlar Payment modelida bo'lsa; agar Sale bo'lsa — Sale ga o'zgartiring
        fields = '__all__'

    def get_group_name(self, obj):
        try:
            sg = obj.student.Sgroup_student.first()
            return sg.group.name if sg and sg.group else None
        except AttributeError:
            return None

    def get_course_name(self, obj):
        try:
            sg = obj.student.Sgroup_student.first()
            return sg.group.course.name if sg and sg.group and sg.group.course else None
        except AttributeError:
            return None

    def get_teacher_name(self, obj):
        try:
            sg = obj.student.Sgroup_student.first()
            if sg and sg.group:
                return ", ".join([t.teacher.get_full_name() for t in sg.group.groupteacher_set.all()])
            return None
        except AttributeError:
            return None


class PaymentChartSerializer(serializers.Serializer):
    """Grafik uchun kunlik ma'lumot"""
    day = serializers.DateField()
    daily_sum = serializers.DecimalField(max_digits=12, decimal_places=2)


class AllPaymentsResponseSerializer(serializers.Serializer):
    """To'liq response strukturasini belgilash uchun (swagger/docs uchun yaxshi)"""
    success = serializers.BooleanField(default=True)
    count = serializers.IntegerField()
    total_payments = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_profit = serializers.DecimalField(max_digits=12, decimal_places=2)
    period = serializers.DictField(child=serializers.CharField())
    chart = serializers.DictField(child=serializers.ListField())
    results = PaymentListSerializer(many=True)

class WithdrawalListSerializer(serializers.ModelSerializer):
    """Jadvalda ko'rsatiladigan yechib olishlar uchun"""
    date = serializers.DateField(source='date', format='%d.%m.%Y')
    student_name = serializers.CharField(source='name', read_only=True, allow_null=True)  # talaba nomi izohdan yoki name dan
    summa = serializers.DecimalField(source='amount', max_digits=12, decimal_places=0)
    izoh = serializers.CharField(source='comment', read_only=True, allow_null=True)
    xodim = serializers.CharField(source='created_by.full_name', read_only=True, allow_null=True)  # yoki accepted_by
    harakat_vaqti = serializers.DateTimeField(source='date', format='%H:%M', read_only=True)
    can_delete = serializers.SerializerMethodField()

    class Meta:
        model = DetailedExpense
        fields = '__all__'

    def get_can_delete(self, obj):
        # Huquq bo'yicha logika (masalan 24 soat ichida o'chirsa bo'ladi)
        return (timezone.now() - obj.date).total_seconds() < 86400  # 24 soat


class WithdrawalChartSerializer(serializers.Serializer):
    """Grafik uchun kunlik chiqimlar"""
    day = serializers.DateField(format='%Y-%m-%d')
    daily_sum = serializers.DecimalField(max_digits=12, decimal_places=0)


class AllWithdrawalsResponseSerializer(serializers.Serializer):
    """To'liq response strukturasini belgilash"""
    success = serializers.BooleanField(default=True)
    total_withdrawals = serializers.DecimalField(max_digits=12, decimal_places=0)
    period = serializers.DictField(child=serializers.CharField(allow_null=True))
    chart = serializers.DictField(child=serializers.ListField())
    results = WithdrawalListSerializer(many=True)



class ExpenseListSerializer(serializers.ModelSerializer):
    # Abdulmajid so'ragan nomlarni (name) chiqarish uchun bularni qo'shing:
    expense_type_name = serializers.CharField(source='expense_type.name', read_only=True)
    branch_name = serializers.CharField(source='branch.name', read_only=True)

    # Siz yozgan boshqa nomlar:
    category_name = serializers.CharField(source='name', read_only=True)
    subcategory_name = serializers.CharField(source='subcategory.name', read_only=True, allow_null=True)
    payment_type_name = serializers.CharField(source='payment_type.name', read_only=True, default="-")

    # Formatlash
    date_formatted = serializers.DateField(source='date', format='%d.%m.%Y', read_only=True)
    time_formatted = serializers.DateTimeField(source='date', format='%H:%M', read_only=True)
    amount_formatted = serializers.DecimalField(source='amount', max_digits=12, decimal_places=0, read_only=True)

    class Meta:
        model = DetailedExpense
        fields = [
            'id',
            'category_name', # Rasmda "Turkum"
            'name',          # Rasmda "Nomi"
            'recipient',     # Rasmda "Oluvchi"
            'payment_type',
            'payment_type_name', # Rasmda "To'lov turi"
            'amount',        # Rasmda "Sum"
            'comment',       # Rasmda "Izoh"
            'created_at',    # Rasmda "Sana"
            'branch_name'
        ]


class ExpenseCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetailedExpense
        fields = '__all__'

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Summa 0 dan katta bo'lishi kerak")
        return value




class TeacherSalaryRuleSerializer(serializers.ModelSerializer):
    """Standart va individual qoidalar uchun (jadvalda ko'rsatiladi)"""
    teacher_name = serializers.CharField(source='teacher.full_name', read_only=True)
    group_name = serializers.CharField(source='group.name', read_only=True, allow_null=True)

    class Meta:
        model = TeacherSalaryRules
        fields = '__all__'


class TeacherSalaryRuleCreateSerializer(serializers.ModelSerializer):
    """Yangi qoida qo'shish uchun"""
    class Meta:
        model = TeacherSalaryRules
        fields = '__all__'

    def validate(self, data):
        if data['effective_from'] > data['effective_to']:
            raise serializers.ValidationError("Boshlanish sanasi tugash sanasidan oldin bo'lishi kerak")
        return data


class TeacherSalaryCalculationSerializer(serializers.ModelSerializer):
    """Hisoblangan maoshlar uchun"""
    teacher_name = serializers.CharField(source='teacher.full_name', read_only=True)
    group_name = serializers.CharField(source='group.name', read_only=True)

    class Meta:
        model = TeacherSalaryCalculations
        fields = '__all__'


class TeacherSalaryMonthlyReportSerializer(serializers.Serializer):
    """Oy bo'yicha jami hisobot"""
    month = serializers.CharField()
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    teacher_count = serializers.IntegerField()
    by_teacher = serializers.ListField(child=serializers.DictField())

# qarzdorlar
class DebtorListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    ism = serializers.CharField()
    telefon = serializers.CharField()
    balans = serializers.DecimalField(max_digits=12, decimal_places=0)
    davr_jami = serializers.DecimalField(max_digits=12, decimal_places=0)
    guruh = serializers.CharField(allow_null=True)
    sana = serializers.CharField()
    izoh = serializers.CharField(allow_null=True)
    holati = serializers.CharField()
    holati_rangi = serializers.CharField()