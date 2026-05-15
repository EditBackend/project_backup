from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_spectacular.utils import extend_schema
from audit.models import AuditLog

# Django ning tayyor Group (Role) modeli
from django.contrib.auth.models import Group

from .models import User, Employee
from .serializers import (
    EmployeeCreateSerializer,
    EmployeeSerializer,
    EmployeeUpdateSerializer,
    RegistrationSerializer
)


# ─── AuditLog helper ─────────────────────────────────────────────

def _log(entity_type, entity_id, action, old_data, new_data, user):
    try:
        # related_name "employee_profile" ga o'zgardi!
        employee = getattr(user, 'employee_profile', None)
        AuditLog.objects.create(
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            old_data=old_data,
            new_data=new_data,
            performed_by=employee,
            performed_by_role=employee.position if employee else 'Tizim / Superadmin',
        )
    except Exception as e:
        print(f"Audit log xatoligi: {e}")  # Xatolikni ko'rish uchun logga yozib qo'ygan ma'qul
        pass


# ════════════════════════════════════════════════════════════════
#  REGISTRATION (Superadmin / Mijoz uchun)
# ════════════════════════════════════════════════════════════════

@extend_schema(tags=["Auth - Mijoz ro'yxatdan o'tishi"])
@api_view(['POST'])
@permission_classes([AllowAny])  # Tizim sotib olayotgan odam uchun ochiq
def registration_view(request):
    serializer = RegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({
            "success": True,
            "message": "Siz muvaffaqiyatli ro'yxatdan o'tdingiz. Tizimga kirishingiz mumkin."
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ════════════════════════════════════════════════════════════════
#  EMPLOYEE (Barcha xodimlar va ularning User profillari)
# ════════════════════════════════════════════════════════════════

@extend_schema(tags=["Employee - Tashkilot xodimlarini boshqarish"])
class EmployeeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.organization:
            return Employee.objects.none()
        return Employee.objects.filter(
            user__organization=user.organization
        ).select_related('user', 'user__branch')

    def get_serializer_class(self):
        if self.action == 'create':
            return EmployeeCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return EmployeeUpdateSerializer
        return EmployeeSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Ma'lumotni saqlaymiz
        employee = serializer.save()

        # Audit log
        _log('employee', employee.id, 'create', None, {
            'action': 'Yangi xodim qo\'shildi',
            'user_id': str(employee.user_id),
            'position': employee.position,
        }, self.request.user)

        # MUHIM: Endi javob qaytarishda 'EmployeeSerializer'dan foydalanamiz
        # Shunda Abdulmajidga 'full_name' bilan birga boradi va 500 xato chiqmaydi
        response_serializer = EmployeeSerializer(employee)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def perform_destroy(self, instance):
        _log('employee', instance.id, 'delete', {
            'user_id': str(instance.user_id),
            'position': instance.position,
        }, None, self.request.user)

        user = instance.user
        instance.delete()
        user.delete()