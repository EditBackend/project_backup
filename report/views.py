from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Sum, Count, Q
from datetime import date, timedelta

from academics.models import StudentBalances, StudentGroupLeaves
from crm.models import CRMLead  # Agar CRMLead modelingiz bo'lsa
from report.serializers import DebtorStudentSerializer


class StudentDebtorsReportAPIView(APIView):
    """ Markazdan qarzdor bo'lgan talabalar ro'yxati va umumiy qarz summasi """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        org = request.user.organization

        # Qarz — balansi 0 dan kichik bo'lgan talabalar
        debtors = StudentBalances.objects.filter(
            organization=org,
            balance__lt=0
        ).select_related('student')

        # Qidiruv (Ixtiyoriy)
        if search := request.GET.get('search'):
            debtors = debtors.filter(
                Q(student__full_name__icontains=search) |
                Q(student__phone_number__icontains=search)
            )

        # Umumiy qarz summasi (Manfiy sonni musbat qilib ko'rsatamiz)
        total_debt = abs(debtors.aggregate(total=Sum('balance'))['total'] or 0)
        debtors_count = debtors.count()

        # Sahifalash (Pagination) o'rniga eng katta qarzdorlarni tepaga chiqaramiz
        debtors = debtors.order_by('balance')[:50]  # Eng ko'p qarzi bor 50 kishi

        return Response({
            "success": True,
            "total_debt": float(total_debt),
            "debtors_count": debtors_count,
            "results": DebtorStudentSerializer(debtors, many=True).data
        })


class StudentChurnReportAPIView(APIView):
    """ O'quvchilarning ketib qolish sabablari (Ketuvchanlik/Churn Rate) hisoboti """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        org = request.user.organization
        start_date = request.GET.get('start_date', (date.today() - timedelta(days=30)).isoformat())
        end_date = request.GET.get('end_date', date.today().isoformat())

        leaves = StudentGroupLeaves.objects.filter(
            organization=org,
            leave_date__range=[start_date, end_date]
        )

        total_left = leaves.count()

        # Sabablar bo'yicha guruhlash
        by_reason = leaves.values(reason_name=getattr('leave_reason__name', "Noma'lum")).annotate(
            student_count=Count('id')
        ).order_by('-student_count')

        # Foizlarni hisoblash
        report_data = []
        for item in by_reason:
            reason = item['reason_name'] or "Sabab ko'rsatilmagan"
            count = item['student_count']
            percentage = round((count / total_left * 100), 2) if total_left > 0 else 0

            report_data.append({
                "reason_name": reason,
                "student_count": count,
                "percentage": percentage
            })

        return Response({
            "period": f"{start_date} dan {end_date} gacha",
            "total_students_left": total_left,
            "reasons_breakdown": report_data
        })


class CRMConversionReportAPIView(APIView):
    """ Marketing tahlili: Qaysi kanaldan qancha o'quvchi keldi va nechta foizi sotib oldi """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        org = request.user.organization
        start_date = request.GET.get('start_date', (date.today() - timedelta(days=30)).isoformat())
        end_date = request.GET.get('end_date', date.today().isoformat())

        leads = CRMLead.objects.filter(
            organization=org,
            created_at__date__range=[start_date, end_date]
        )

        total_leads = leads.count()

        # Kanallar bo'yicha guruhlash (Instagram, Telegram, Tavsiya...)
        by_source = leads.values(source_name=getattr('source__name', "Noma'lum")).annotate(
            total=Count('id'),
            converted=Count('id', filter=Q(status='converted'))  # status='converted' talaba bo'lganlarni bildiradi
        ).order_by('-total')

        report_data = []
        for item in by_source:
            source = item['source_name'] or "Boshqa"
            total = item['total']
            converted = item['converted']
            conversion_rate = round((converted / total * 100), 2) if total > 0 else 0

            report_data.append({
                "source_name": source,
                "total_leads": total,
                "converted_leads": converted,
                "conversion_rate": conversion_rate
            })

        return Response({
            "period": f"{start_date} dan {end_date} gacha",
            "overall_leads": total_leads,
            "overall_converted": leads.filter(status='converted').count(),
            "sources_breakdown": report_data
        })