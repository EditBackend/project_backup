from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from .models import User, Employee, Role, RolePermission, UserRole
from .serializers import (
    UserSerializer, EmployeeCreateSerializer, RoleSerializer,
    RolePermissionSerializer, UserRoleSerializer,EmployeeSerializer,EmployeeUpdateSerializer
)
from audit.models import AuditLog


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


# ════════════════════════════════════════════════════════════════
#  USER
# ════════════════════════════════════════════════════════════════

@extend_schema(tags=["User - Foydalanuvchilarni ko'rish"])
class UserViewSet(viewsets.ModelViewSet):
    queryset         = User.objects.all()
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        _log('user', user.id, 'create', None, {
            'username':  user.username,
            'full_name': user.full_name,
            'phone':     user.phone,
        }, self.request.user)

    def perform_update(self, serializer):
        old = {
            'username':  serializer.instance.username,
            'full_name': serializer.instance.full_name,
            'phone':     serializer.instance.phone,
        }
        user = serializer.save()
        _log('user', user.id, 'update', old, {
            'username':  user.username,
            'full_name': user.full_name,
            'phone':     user.phone,
        }, self.request.user)

    def perform_destroy(self, instance):
        _log('user', instance.id, 'delete', {
            'username':  instance.username,
            'full_name': instance.full_name,
            'phone':     instance.phone,
        }, None, self.request.user)
        instance.delete()


# ════════════════════════════════════════════════════════════════
#  EMPLOYEE
# ════════════════════════════════════════════════════════════════



from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from .serializers import RegistrationSerializer

@api_view(['POST'])
@permission_classes([AllowAny]) # Hamma ariza topshira olishi kerak
def registration_view(request):
    serializer = RegistrationSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            "message": "Arizangiz qabul qilindi. Admin tasdiqlashini kuting."
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=["Employee - Barcha ishchilarni ko'rish"])
class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.select_related('user').all()   # Bu yerda select_related yaxshi
    serializer_class = EmployeeSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return EmployeeCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return EmployeeUpdateSerializer
        return EmployeeSerializer


    def perform_create(self, serializer):
        employee = serializer.save()
        _log('user', employee.id, 'create', None, {
            'action':   'Xodim yaratildi',
            'user_id':  str(employee.user_id),
            'position': employee.position,
        }, self.request.user)

    # def perform_update(self, serializer):
    #     old = {'position': serializer.instance.position, 'is_active': serializer.instance.is_active}
    #     employee = serializer.save()
    #     _log('user', employee.id, 'update', old, {
    #         'position':  employee.position,
    #         'is_active': employee.is_active,
    #     }, self.request.user)

    def perform_destroy(self, instance):
        _log('user', instance.id, 'delete', {
            'user_id':  str(instance.user_id),
            'position': instance.position,
        }, None, self.request.user)
        instance.delete()




# ════════════════════════════════════════════════════════════════
#  ROLE
# ════════════════════════════════════════════════════════════════

@extend_schema(tags=["Role - Ishchilarga mavjud rollarni ko'rish"])
class RoleViewSet(viewsets.ModelViewSet):
    queryset         = Role.objects.all()
    serializer_class = RoleSerializer

    def perform_create(self, serializer):
        role = serializer.save()
        _log('user', role.id, 'create', None, {'name': role.name}, self.request.user)

    def perform_update(self, serializer):
        old  = {'name': serializer.instance.name}
        role = serializer.save()
        _log('user', role.id, 'update', old, {'name': role.name}, self.request.user)

    def perform_destroy(self, instance):
        _log('user', instance.id, 'delete', {'name': instance.name}, None, self.request.user)
        instance.delete()


# ════════════════════════════════════════════════════════════════
#  ROLE PERMISSION
# ════════════════════════════════════════════════════════════════

@extend_schema(tags=["RolePermission - Rollarga berilgan ruxsatlarni ko'rish"])
class RolePermissionViewSet(viewsets.ModelViewSet):
    queryset         = RolePermission.objects.all()
    serializer_class = RolePermissionSerializer

    def perform_create(self, serializer):
        rp = serializer.save()
        _log('user', rp.id, 'create', None, {
            'role_id':       str(rp.role_id),
            'permission_id': str(rp.permission_id),
        }, self.request.user)

    def perform_destroy(self, instance):
        _log('user', instance.id, 'delete', {
            'role_id':       str(instance.role_id),
            'permission_id': str(instance.permission_id),
        }, None, self.request.user)
        instance.delete()


# ════════════════════════════════════════════════════════════════
#  USER ROLE
# ════════════════════════════════════════════════════════════════

@extend_schema(tags=["UserRole - Foydalanuvchiga berilgan ruxsatlarni ko'rish"])
class UserRoleViewSet(viewsets.ModelViewSet):
    queryset         = UserRole.objects.all()
    serializer_class = UserRoleSerializer

    def perform_create(self, serializer):
        ur = serializer.save()
        _log('user', ur.id, 'create', None, {
            'user_id': str(ur.user_id),
            'role_id': str(ur.role_id),
        }, self.request.user)

    def perform_destroy(self, instance):
        _log('user', instance.id, 'delete', {
            'user_id': str(instance.user_id),
            'role_id': str(instance.role_id),
        }, None, self.request.user)
        instance.delete()