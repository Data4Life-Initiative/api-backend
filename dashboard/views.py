from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from authentication.permissions import IsDataEntryAdmin
from core.models import PatientHistoricLocation
from dashboard.serializers import StatSerializer
from patient.serializers import PatientHistoricLocationSerializer


class StatsAPIView(generics.GenericAPIView):
    """
    API to retrieve data entry admin dashboard disease stats
    """
    serializer_class = StatSerializer

    def get(self, request):
        data = {
            "immunized": 10,
            "naturally_immune": 45,
            "currently_infected": 80
        }

        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data)


class MapDataAPIView(generics.GenericAPIView):
    """
    Patient historic locations that are recorded within past `x` seconds
    """
    serializer_class = PatientHistoricLocationSerializer
    permission_classes = (IsAuthenticated, IsDataEntryAdmin,)

    def get(self, request):
        historic_locations = PatientHistoricLocation.objects.filter(recorded_date_time__gte=timezone.now() - timedelta(
            seconds=settings.HISTORIC_LOCATION_EXPIRY_IN_SECONDS)).order_by('-recorded_date_time')
        serializer = self.serializer_class(historic_locations, many=True)

        return Response(serializer.data)


class PatientHistoricLocationSyncConsentQRCodeView(generics.GenericAPIView):
    def get(self, request):
        """
        For returning the URL for QR code for obtaining explicit
        consent from a patient and retrieving the historic locations

        :param request:
        :return:
        """
        return Response({"qr_code_url": settings.HISTORIC_LOCATION_SYNC_CONSENT_QR_CODE_URL})
