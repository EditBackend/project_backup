from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Count
from datetime import datetime
from rest_framework.views import APIView
from django.contrib.auth.hashers import check_password
from audit.models import AuditLog
from .models import (
    Organizations, OrganizationSettings, Subscriptions, Branch,
    ExamSettings, LandingPage, LandingPageSubmission, SuperAdmin
)
from rest_framework.permissions import AllowAny
from .models import SuperAdmin
from accounts.models import Employee
from .serializers import (
    OrganizationSerializer, OrganizationCreateSerializer,
    OrganizationSettingsSerializer, SubscriptionSerializer,
    BranchSerializer, ExamSettingsSerializer,
    BillingSubscriptionSerializer, BillingCreateSerializer,
    LandingPageSerializer, LandingPageCreateSerializer,
    LandingPageSubmissionSerializer, LandingPageSubmissionCreateSerializer,
    SuperAdminSerializer
)

from accounts.models import User

# views.py
class OrganizationJoinView(APIView):
    def post(self, request):
        org_username = request.data.get('org_username')
        org_password = request.data.get('org_password')
        user = request.user

        org = Organizations.objects.filter(
            org_username=org_username,
            org_password=org_password
        ).first()

        if not org:
            return Response({"error": "Login yoki parol xato"}, status=404)

        # Foydalanuvchini ushbu tashkilotga ulaymiz
        employee, created = Employee.objects.get_or_create(user=user)
        employee.organization_id = org
        employee.role = 'admin' # Kirgan odam admin bo'ladi
        employee.save()

        return Response({
            "success": True,
            "message": f"{org.name}ga kirdingiz",
            "org_id": org.id
        })

# 1. SuperAdmin yaratish (POST)
class SuperAdminCreateView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = SuperAdminSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "SuperAdmin muvaffaqiyatli yaratildi"
            }, status=status.HTTP_201_CREATED)
        return Response({
            "success": False,
            "error": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

# 2. Login (POST)
from rest_framework_simplejwt.tokens import RefreshToken # JWT uchun
from django.contrib.auth.hashers import check_password
from .models import SuperAdmin

class SuperAdminLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        try:
            admin = SuperAdmin.objects.get(username=username)

            if check_password(password, admin.password):
                # JWT tokenni qo'lda yasaymiz
                refresh = RefreshToken.for_user(admin)

                # Payload ichiga qo'shimcha ma'lumot qo'shish (ixtiyoriy)
                refresh['username'] = admin.username

                return Response({
                    "success": True,
                    "message": "Login muvaffaqiyatli",
                    "access": str(refresh.access_token), # Asosiy token
                    "refresh": str(refresh),             # Yangilash uchun token
                    "data": {
                        "id": admin.id,
                        "username": admin.username
                    }
                }, status=status.HTTP_200_OK)
            else:
                return Response({"success": False, "error": "Parol noto'g'ri"}, status=status.HTTP_401_UNAUTHORIZED)

        except SuperAdmin.DoesNotExist:
            return Response({"success": False, "error": "Foydalanuvchi topilmadi"}, status=status.HTTP_404_NOT_FOUND)




# ─── AuditLog helper ─────────────────────────────────────────────

def _log(entity_type, entity_id, action, old_data, new_data, user):
    try:
        employee = user.employee if hasattr(user, 'employee') else None
        AuditLog.objects.create(
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            old_data=old_data,
            new_action=new_data,
            performed_by=employee,
            performed_by_role=employee.position if employee else '',
        )
    except Exception:
        pass

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def organization_create_view(request):
    user = request.user

    # 1. Employee profilini va uning holatini tekshirish
    employee = getattr(user, 'employee', None)

    if not employee or not employee.is_approved:
        return Response(
            {"detail": "Sizning arizangiz hali tasdiqlanmagan. Admin tasdiqlashini kuting."},
            status=status.HTTP_403_FORBIDDEN
        )

    # 2. Agar tasdiqlangan bo'lsa, tashkilot yaratish
    serializer = OrganizationCreateSerializer(data=request.data)
    if serializer.is_valid():
        # created_by ga employeeni biriktiramiz
        serializer.save(created_by=employee)

        # Tasdiqdan o'tgach qayta so'rov yubormasligi uchun (ixtiyoriy)
        # employee.is_approved = True (o'zi shundoq ham True)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ════════════════════════════════════════════════════════════════
#  ORGANIZATIONS
# ════════════════════════════════════════════════════════════════

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .models import Organizations
from .serializers import OrganizationSerializer, OrganizationCreateSerializer
from accounts.models import Employee
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def organization_list_create(request):
    user = request.user

    # ================= GET SO'ROVI =================
    if request.method == 'GET':
        # 1. Kirgan odam SuperAdminmi?
        is_superadmin = SuperAdmin.objects.filter(id=user.id).exists()

        if is_superadmin:
            # SuperAdmin hammasini ko'radi
            orgs = Organizations.objects.all()
        else:
            # Oddiy user faqat o'zi a'zo bo'lgan (yoki yaratgan) tashkilotni ko'radi
            employee = Employee.objects.filter(user=user).first()
            if employee and employee.organization_id:
                orgs = Organizations.objects.filter(id=employee.organization_id.id)
            else:
                # Agar hali birorta ham org ga a'zo bo'lmasa, bo'sh ro'yxat qaytaradi
                orgs = Organizations.objects.none()

        serializer = OrganizationSerializer(orgs, many=True)
        return Response(serializer.data)

    # ================= POST SO'ROVI =================
    elif request.method == 'POST':
        # Tashkilot yaratish mantiqi shu yerda bo'ladi
        serializer = OrganizationSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            # Muvaffaqiyatli saqlansa, 201 status va ma'lumot qaytadi
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # Agar yuborilgan ma'lumotda xato bo'lsa (validatsiyadan o'tmasa), 400 status va xatolar qaytadi
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def organization_detail(request, pk):
    org = get_object_or_404(Organizations, pk=pk)

    if request.method == 'GET':
        return Response(OrganizationSerializer(org).data)

    elif request.method == 'PUT':
        # Employeeni aniq qidirib olamiz
        employee = Employee.objects.filter(user=request.user).first()

        serializer = OrganizationSerializer(org, data=request.data, partial=True)
        if serializer.is_valid():
            # Agar employee topilsa o'shani beramiz, bo'lmasa None
            serializer.save(updated_by=employee)

            _log('other', org.id, 'update', old_data, {
                'name': org.name,
                'status': org.status,
            }, request.user)

            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        _log('other', org.id, 'delete', {'name': org.name}, None, request.user)
        org.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ════════════════════════════════════════════════════════════════
#  ORGANIZATION SETTINGS
# ════════════════════════════════════════════════════════════════

@api_view(['GET', 'PUT'])
def organization_settings(request, org_pk):
    org                  = get_object_or_404(Organizations, pk=org_pk)
    settings, created    = OrganizationSettings.objects.get_or_create(organization=org)

    if request.method == 'GET':
        return Response(OrganizationSettingsSerializer(settings).data)

    serializer = OrganizationSettingsSerializer(settings, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()

        _log('other', org.id, 'update', None, {
            'action': 'Tashkilot sozlamalari yangilandi',
        }, request.user)

        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ════════════════════════════════════════════════════════════════
#  SUBSCRIPTIONS
# ════════════════════════════════════════════════════════════════

@api_view(['GET', 'POST'])
def subscription_list_create(request, org_pk):
    org = get_object_or_404(Organizations, pk=org_pk)

    if request.method == 'GET':
        subs = Subscriptions.objects.filter(organization_id=org)
        return Response(SubscriptionSerializer(subs, many=True).data)

    serializer = SubscriptionSerializer(data=request.data)
    if serializer.is_valid():
        sub = serializer.save(organization_id=org)

        _log('other', sub.id, 'create', None, {
            'action':     'Obuna yaratildi',
            'plan_type':  sub.plan_type,
            'start_date': str(sub.start_date),
            'end_date':   str(sub.end_date),
            'status':     sub.status,
        }, request.user)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def subscription_detail(request, org_pk, pk):
    sub = get_object_or_404(Subscriptions, pk=pk, organization_id__pk=org_pk)

    if request.method == 'GET':
        return Response(SubscriptionSerializer(sub).data)

    elif request.method == 'PUT':
        old_data   = {'status': sub.status, 'end_date': str(sub.end_date)}
        serializer = SubscriptionSerializer(sub, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()

            _log('other', sub.id, 'update', old_data, {
                'status':   sub.status,
                'end_date': str(sub.end_date),
            }, request.user)

            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        _log('other', sub.id, 'delete', {'plan_type': sub.plan_type, 'status': sub.status}, None, request.user)
        sub.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ════════════════════════════════════════════════════════════════
#  BRANCHES
# ════════════════════════════════════════════════════════════════

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated]) # Token bo'lishi shart
def branch_list_create(request, org_pk):
    user = request.user
    # 1. Avval so'rov yuborgan odamning o'zini tashkilotini aniqlaymiz
    employee = Employee.objects.filter(user=user).first()
    is_superadmin = SuperAdmin.objects.filter(id=user.id).exists()

    # 2. Xavfsizlik tekshiruvi:
    # Agar foydalanuvchi SuperAdmin bo'lmasa VA uning tashkiloti URL'dagi org_pk ga teng bo'lmasa - ruxsat bermaymiz!
    if not is_superadmin:
        if not employee or str(employee.organization_id.id) != str(org_pk):
            return Response(
                {"error": "Siz faqat o'z tashkilotingiz filiallari bilan ishlay olasiz!"},
                status=status.HTTP_403_FORBIDDEN
            )

    # Endi bu 'org' haqiqatdan ham foydalanuvchiga tegishli ekanligi aniq
    org = get_object_or_404(Organizations, pk=org_pk)

    # --- GET: Faqat shu tashkilot filiallarini chiqarish ---
    if request.method == 'GET':
        is_active = request.query_params.get('is_active')
        branches = Branch.objects.filter(organization=org) # Mana shu yerda filtr ishlayapti

        if is_active is not None:
            branches = branches.filter(is_active=is_active.lower() == 'true')

        return Response(BranchSerializer(branches, many=True).data)

    # --- POST: Filial yaratish ---
    if request.method == 'POST':
        serializer = BranchSerializer(data=request.data)
        if serializer.is_valid():
            # serializer.save ichida org.id emas, org obyektini o'zini berish kerak
            branch = serializer.save(organization=org)

            _log('other', branch.id, 'create', None, {
                'action': 'Filial yaratildi',
                'name':   branch.name,
                'phone':  branch.phone,
            }, request.user)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def branch_detail(request, org_pk, pk):
    branch = get_object_or_404(Branch, pk=pk, organization_id__pk=org_pk)

    if request.method == 'GET':
        return Response(BranchSerializer(branch).data)

    elif request.method == 'PUT':
        old_data   = {'name': branch.name, 'is_active': branch.is_active}
        serializer = BranchSerializer(branch, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()

            _log('other', branch.id, 'update', old_data, {
                'name':      branch.name,
                'is_active': branch.is_active,
            }, request.user)

            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        _log('other', branch.id, 'delete', {'name': branch.name}, None, request.user)
        branch.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ════════════════════════════════════════════════════════════════
#  EXAM SETTINGS
# ════════════════════════════════════════════════════════════════

@api_view(['GET', 'PUT'])
def exam_settings(request, org_pk):
    org               = get_object_or_404(Organizations, pk=org_pk)
    settings, created = ExamSettings.objects.get_or_create(organization=org)

    if request.method == 'GET':
        return Response(ExamSettingsSerializer(settings).data)

    serializer = ExamSettingsSerializer(settings, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()

        _log('other', org.id, 'update', None, {
            'action': 'Imtihon sozlamalari yangilandi',
        }, request.user)

        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ════════════════════════════════════════════════════════════════
#  LANDING PAGES
# ════════════════════════════════════════════════════════════════

@api_view(['GET', 'POST'])
def landing_page_list_create(request, org_pk):
    org = get_object_or_404(Organizations, pk=org_pk)

    if request.method == 'GET':
        is_active = request.query_params.get('is_active')
        source    = request.query_params.get('source')
        pages     = LandingPage.objects.filter(organization=org)
        if is_active is not None:
            pages = pages.filter(is_active=is_active.lower() == 'true')
        if source:
            pages = pages.filter(source=source)
        return Response(LandingPageSerializer(pages, many=True).data)

    serializer = LandingPageCreateSerializer(data=request.data)
    if serializer.is_valid():
        page = serializer.save(organization=org)

        _log('other', page.id, 'create', None, {
            'action': 'Landing page yaratildi',
            'name':   page.name,
            'slug':   page.slug,
            'source': page.source,
        }, request.user)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def landing_page_detail(request, org_pk, pk):
    page = get_object_or_404(LandingPage, pk=pk, organization__pk=org_pk)

    if request.method == 'GET':
        return Response(LandingPageSerializer(page).data)

    elif request.method == 'PUT':
        old_data   = {'name': page.name, 'is_active': page.is_active}
        serializer = LandingPageSerializer(page, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()

            _log('other', page.id, 'update', old_data, {
                'name':      page.name,
                'is_active': page.is_active,
            }, request.user)

            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        _log('other', page.id, 'delete', {'name': page.name, 'slug': page.slug}, None, request.user)
        page.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def landing_page_by_slug(request, slug):
    page = get_object_or_404(LandingPage, slug=slug, is_active=True)
    return Response(LandingPageSerializer(page).data)


# ════════════════════════════════════════════════════════════════
#  LANDING PAGE SUBMISSIONS
# ════════════════════════════════════════════════════════════════

@api_view(['GET', 'POST'])
def submission_list_create(request, org_pk, page_pk):
    page = get_object_or_404(LandingPage, pk=page_pk, organization__pk=org_pk)

    if request.method == 'GET':
        submissions = LandingPageSubmission.objects.filter(landing_page=page)
        return Response(LandingPageSubmissionSerializer(submissions, many=True).data)

    serializer = LandingPageSubmissionCreateSerializer(data=request.data)
    if serializer.is_valid():
        sub = serializer.save(landing_page=page)

        _log('other', sub.id, 'create', None, {
            'action':    'Submission yaratildi',
            'full_name': sub.full_name,
            'phone':     sub.phone,
        }, request.user)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def public_submission_create(request, slug):
    """Public endpoint — talabalar ro'yxatdan o'tishi (AuditLog shart emas)"""
    page = get_object_or_404(LandingPage, slug=slug, is_active=True)
    serializer = LandingPageSubmissionCreateSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(landing_page=page)
        return Response({
            'message': "Arizangiz qabul qilindi! Tez orada siz bilan bog'lanamiz.",
            'data':    serializer.data,
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'DELETE'])
def submission_detail(request, org_pk, page_pk, pk):
    submission = get_object_or_404(
        LandingPageSubmission, pk=pk,
        landing_page__pk=page_pk, landing_page__organization__pk=org_pk,
    )

    if request.method == 'GET':
        return Response(LandingPageSubmissionSerializer(submission).data)

    _log('other', submission.id, 'delete', {
        'full_name': submission.full_name, 'phone': submission.phone,
    }, None, request.user)
    submission.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# ════════════════════════════════════════════════════════════════
#  STATISTIKA
# ════════════════════════════════════════════════════════════════

@api_view(['GET'])
def landing_statistics(request, org_pk):
    org   = get_object_or_404(Organizations, pk=org_pk)
    pages = LandingPage.objects.filter(organization=org)

    stats = [{
        'id':                page.id,
        'name':              page.name,
        'slug':              page.slug,
        'source':            page.source,
        'submissions_count': page.submissions.count(),
        'is_active':         page.is_active,
    } for page in pages]

    return Response(stats)


# ════════════════════════════════════════════════════════════════
#  BILLING
# ════════════════════════════════════════════════════════════════

@api_view(['GET'])
def billing_dashboard(request, org_pk):
    org         = get_object_or_404(Organizations, pk=org_pk)
    current_sub = Subscriptions.objects.filter(organization_id=org, status='active').order_by('-end_date').first()
    all_subs    = Subscriptions.objects.filter(organization_id=org)
    total_spent = all_subs.aggregate(total=Sum('price'))['total'] or 0

    days_remaining = 0
    if current_sub and current_sub.end_date:
        delta          = current_sub.end_date.date() - datetime.now().date()
        days_remaining = delta.days if delta.days > 0 else 0

    org_status = org.status
    if days_remaining == 0:
        org_status = 'expired'
    elif 0 < days_remaining <= 7:
        org_status = 'expires'

    return Response({
        'current_subscription': BillingSubscriptionSerializer(current_sub).data if current_sub else None,
        'total_subscriptions':  all_subs.count(),
        'total_spent':          total_spent,
        'next_payment_date':    current_sub.end_date if current_sub else None,
        'days_remaining':       days_remaining,
        'status':               org_status,
    })


@api_view(['GET'])
def billing_history(request, org_pk):
    org           = get_object_or_404(Organizations, pk=org_pk)
    subscriptions = Subscriptions.objects.filter(organization_id=org).order_by('-created_at')
    return Response(BillingSubscriptionSerializer(subscriptions, many=True).data)


@api_view(['POST'])
def billing_pay(request, org_pk):
    org        = get_object_or_404(Organizations, pk=org_pk)
    serializer = BillingCreateSerializer(data=request.data)
    if serializer.is_valid():
        subscription = serializer.save(organization_id=org)

        org.status = 'active'
        org.save()

        _log('other', subscription.id, 'create', None, {
            'action':    'To\'lov amalga oshirildi',
            'plan_type': subscription.plan_type,
            'price':     str(subscription.price),
            'end_date':  str(subscription.end_date),
        }, request.user)

        return Response({
            'message':      "To'lov muvaffaqiyatli amalga oshirildi!",
            'subscription': BillingSubscriptionSerializer(subscription).data,
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def billing_plans(request):
    plans = [
        {
            'plan_type': 'basic', 'name': 'Asosiy',
            'price_1month': 500000, 'price_3months': 1350000,
            'price_6months': 2400000, 'price_12months': 4500000,
            'features': ['50 tagacha guruh', '200 tagacha talaba', '5 ta filial', 'Asosiy hisobotlar'],
        },
        {
            'plan_type': 'premium', 'name': 'Premium',
            'price_1month': 1000000, 'price_3months': 2700000,
            'price_6months': 4800000, 'price_12months': 9000000,
            'features': ['Cheksiz guruh', 'Cheksiz talaba', 'Cheksiz filial',
                         'Barcha hisobotlar', 'SMS xizmati', 'Prioritet qo\'llab-quvvatlash'],
        },
        {
            'plan_type': 'enterprise', 'name': 'Korporativ',
            'price_1month': 2000000, 'price_3months': 5400000,
            'price_6months': 9600000, 'price_12months': 18000000,
            'features': ['Premium barcha imkoniyatlari', 'Maxsus integratsiyalar',
                         'Shaxsiy menejer', 'API kirish', 'White-label imkoniyati'],
        },
    ]
    return Response(plans)


@api_view(['GET'])
def billing_current(request, org_pk):
    org         = get_object_or_404(Organizations, pk=org_pk)
    current_sub = Subscriptions.objects.filter(organization_id=org, status='active').order_by('-end_date').first()

    if not current_sub:
        return Response({'message': 'Faol obuna topilmadi'}, status=status.HTTP_404_NOT_FOUND)

    return Response(BillingSubscriptionSerializer(current_sub).data)



