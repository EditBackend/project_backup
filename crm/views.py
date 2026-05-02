from drf_spectacular.utils import extend_schema
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from audit.models import AuditLog
from .models import (
    CRMSource, CRMPipelines, CRMLead,
    CRMActivity, CRMLeadsHistory,
    CRMLostReason, CRMLeadLost, CRMLeadNotes,
)
from .serializers import (
    CRMSourceSerializer, CRMPipelinesSerializer, CRMLeadSerializer,
    CRMActivitySerializer, CRMLeadsHistorySerializer,
    CRMLostReasonSerializer, CRMLeadLostSerializer, CRMLeadNotesSerializer,
)
from rest_framework import viewsets

from .models import CrmSection
from .serializers import CrmSectionSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import LeadForm,FormField
from .serializers import LeadFormSerializer, LeadFormCreateSerializer


class LeadFormViewSet(viewsets.ModelViewSet):
    queryset = LeadForm.objects.prefetch_related('fields').all()
    serializer_class = LeadFormSerializer

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return LeadFormCreateSerializer
        return LeadFormSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save(created_by=request.user)

        # Javobda to'liq ma'lumot (fields bilan) qaytarish
        output_serializer = LeadFormSerializer(instance)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    # Forma nusxasini yaratish
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        form = self.get_object()
        new_form = LeadForm.objects.create(
            name=f"{form.name} (nusxa)",
            type=form.type,
            branch=form.branch,
            pipeline=form.pipeline,
            source=form.source,
            created_by=request.user
        )

        for field in form.fields.all():
            FormField.objects.create(
                lead_form=new_form,
                label=field.label,
                field_type=field.field_type,
                is_required=field.is_required,
                order=field.order,
                options=field.options
            )

        serializer = LeadFormSerializer(new_form)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # Field turlarini olish (select uchun)
    @action(detail=False, methods=['get'])
    def field_types(self, request):
        choices = [
            {"value": k, "label": v}
            for k, v in FormField.FIELD_TYPE_CHOICES
        ]
        return Response(choices)




class CrmSectionViewSet(viewsets.ModelViewSet):
    queryset = CrmSection.objects.all()
    serializer_class = CrmSectionSerializer
    permission_classes = [IsAuthenticated]  # ixtiyoriy

    def get_queryset(self):
        queryset = super().get_queryset()
        pipeline_id = self.request.query_params.get('pipeline')

        if pipeline_id:
            queryset = queryset.filter(pipeline_id=pipeline_id)

        return queryset


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
#  CRM SOURCE
# ════════════════════════════════════════════════════════════════

@extend_schema(tags=["CRMSource - Leadlar qayerdan kelyapti"])
class CRMSourceViewSet(ModelViewSet):
    queryset           = CRMSource.objects.all()
    serializer_class   = CRMSourceSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        obj = serializer.save()
        _log('lead', obj.id, 'create', None, {
            'action': 'CRM manba yaratildi',
            'name':   obj.name,
        }, self.request.user)

    def perform_update(self, serializer):
        old = {'name': serializer.instance.name}
        obj = serializer.save()
        _log('lead', obj.id, 'update', old, {'name': obj.name}, self.request.user)

    def perform_destroy(self, instance):
        _log('lead', instance.id, 'delete', {'name': instance.name}, None, self.request.user)
        instance.delete()


# ════════════════════════════════════════════════════════════════
#  CRM PIPELINES
# ════════════════════════════════════════════════════════════════

@extend_schema(tags=["CRMPipelines - Lead varonkasini ko'rish"])
class CRMPipelinesViewSet(ModelViewSet):
    queryset           = CRMPipelines.objects.all()
    serializer_class   = CRMPipelinesSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        obj = serializer.save()
        _log('lead', obj.id, 'create', None, {
            'action':   'Pipeline yaratildi',
            'name':     obj.name,
            'position': obj.position,
        }, self.request.user)

    def perform_update(self, serializer):
        old = {'name': serializer.instance.name, 'position': serializer.instance.position}
        obj = serializer.save()
        _log('lead', obj.id, 'update', old, {
            'name':     obj.name,
            'position': obj.position,
        }, self.request.user)

    def perform_destroy(self, instance):
        _log('lead', instance.id, 'delete',
             {'name': instance.name, 'position': instance.position},
             None, self.request.user)
        instance.delete()


# ════════════════════════════════════════════════════════════════
#  CRM LEAD
# ════════════════════════════════════════════════════════════════

@extend_schema(tags=["CRMLead - Leadlarni ko'rish"])
class CRMLeadViewSet(ModelViewSet):
    queryset           = CRMLead.objects.all()
    serializer_class   = CRMLeadSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(assigned_to=self.request.user)

    def perform_update(self, serializer):
        old = {
            'full_name':    serializer.instance.full_name,
            'phone_number': serializer.instance.phone_number,
            'status':       serializer.instance.status,
            'pipeline_id':  str(serializer.instance.pipline_id) if hasattr(serializer.instance, 'pipline_id') else None,
        }
        obj = serializer.save()
        _log('lead', obj.id, 'update', old, {
            'full_name':    obj.full_name,
            'phone_number': obj.phone_number,
            'status':       obj.status,
            'pipeline_id':  str(obj.pipline_id) if hasattr(obj, 'pipline_id') else None,
        }, self.request.user)

    def perform_destroy(self, instance):
        # MUHIM: _log parametrlarini tekshiring.
        # Agar None yuborish kerak bo'lsa ham, {} (bo'sh dict) yuborish xavfsizroq.
        _log('lead', instance.id, 'delete', {
            'full_name':    instance.full_name,
            'phone_number': instance.phone_number,
            'status':       instance.status,
        }, {}, self.request.user) # None o'rniga {} yubordik
        instance.delete()


# ════════════════════════════════════════════════════════════════
#  CRM ACTIVITY
# ════════════════════════════════════════════════════════════════

@extend_schema(tags=["CRMActivity - Leadlar ustida bajarilgan barcha ishlarni ko'rsatish"])
class CRMActivityViewSet(ModelViewSet):
    queryset           = CRMActivity.objects.all()
    serializer_class   = CRMActivitySerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        obj = serializer.save()
        _log('lead', obj.lead_id, 'update', None, {
            'action':        'Faoliyat qo\'shildi',
            'activity_type': obj.activity_type,
            'result':        obj.result,
        }, self.request.user)

    def perform_update(self, serializer):
        old = {'activity_type': serializer.instance.activity_type, 'result': serializer.instance.result}
        obj = serializer.save()
        _log('lead', obj.lead_id, 'update', old, {
            'activity_type': obj.activity_type,
            'result':        obj.result,
        }, self.request.user)

    def perform_destroy(self, instance):
        _log('lead', instance.lead_id, 'update',
             {'activity_type': instance.activity_type, 'result': instance.result},
             {'action': 'Faoliyat o\'chirildi'},
             self.request.user)
        instance.delete()


# ════════════════════════════════════════════════════════════════
#  CRM LEADS HISTORY
#  (tarix faqat yoziladi — o'chirish/yangilash shart emas)
# ════════════════════════════════════════════════════════════════

@extend_schema(tags=["CRMLeadsHistory - Lead ni butun tarixini ko'rsatish"])
class CRMLeadsHistoryViewSet(ModelViewSet):
    queryset           = CRMLeadsHistory.objects.all()
    serializer_class   = CRMLeadsHistorySerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        obj = serializer.save()
        _log('lead', obj.lead_id, 'update', None, {
            'action':          'Pipeline o\'zgartirildi',
            'old_pipeline_id': str(obj.old_pipeline_id) if obj.old_pipeline_id else None,
            'new_pipeline_id': str(obj.new_pipeline_id) if obj.new_pipeline_id else None,
        }, self.request.user)


# ════════════════════════════════════════════════════════════════
#  CRM LOST REASON
# ════════════════════════════════════════════════════════════════

@extend_schema(tags=["CRMLostReason - Leadlar ni ketib qolish sabablari kiritish"])
class CRMLostReasonViewSet(ModelViewSet):
    queryset           = CRMLostReason.objects.all()
    serializer_class   = CRMLostReasonSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        obj = serializer.save()
        _log('lead', obj.id, 'create', None, {
            'action': 'Ketish sababi yaratildi',
            'name':   obj.name,
        }, self.request.user)

    def perform_update(self, serializer):
        old = {'name': serializer.instance.name}
        obj = serializer.save()
        _log('lead', obj.id, 'update', old, {'name': obj.name}, self.request.user)

    def perform_destroy(self, instance):
        _log('lead', instance.id, 'delete', {'name': instance.name}, None, self.request.user)
        instance.delete()


# ════════════════════════════════════════════════════════════════
#  CRM LEAD LOST
# ════════════════════════════════════════════════════════════════

@extend_schema(tags=["CRMLeadLost - Leadlarni ketib qolishlarini ko'rish"])
class CRMLeadLostViewSet(ModelViewSet):
    queryset           = CRMLeadLost.objects.all()
    serializer_class   = CRMLeadLostSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        obj = serializer.save()
        _log('lead', obj.lead_id, 'update', None, {
            'action':    'Lead yo\'qotildi',
            'reason_id': str(obj.reason_id) if obj.reason_id else None,
            'comment':   obj.comment,
        }, self.request.user)

    def perform_destroy(self, instance):
        _log('lead', instance.lead_id, 'update',
             {'reason_id': str(instance.reason_id), 'comment': instance.comment},
             {'action': 'Lead lost yozuvi o\'chirildi'},
             self.request.user)
        instance.delete()


# ════════════════════════════════════════════════════════════════
#  CRM LEAD NOTES
# ════════════════════════════════════════════════════════════════

@extend_schema(tags=["CRMLeadNotes - Lead ga yozilgan izohlar"])
class CRMLeadNotesViewSet(ModelViewSet):
    queryset           = CRMLeadNotes.objects.all()
    serializer_class   = CRMLeadNotesSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        obj = serializer.save()
        _log('lead', obj.lead_id, 'update', None, {
            'action': 'Izoh qo\'shildi',
            'note':   obj.note[:100],
        }, self.request.user)

    def perform_update(self, serializer):
        old = {'note': serializer.instance.note[:100]}
        obj = serializer.save()
        _log('lead', obj.lead_id, 'update', old, {'note': obj.note[:100]}, self.request.user)

    def perform_destroy(self, instance):
        _log('lead', instance.lead_id, 'update',
             {'note': instance.note[:100]},
             {'action': 'Izoh o\'chirildi'},
             self.request.user)
        instance.delete()


