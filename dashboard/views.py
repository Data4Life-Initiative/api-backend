from django.conf import settings
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from authentication.permissions import IsDataEntryAdmin
from core.models import PatientHistoricLocation
from dashboard.serializers import StatSerializer
from patient.serializers import PatientHistoricLocationSerializer


class StatsAPIView(generics.GenericAPIView):
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
    serializer_class = PatientHistoricLocationSerializer
    permission_classes = (IsAuthenticated, IsDataEntryAdmin,)

    def get(self, request):
        historic_locations = PatientHistoricLocation.objects.all()
        serializer = self.serializer_class(historic_locations, many=True)

        return Response(serializer.data)


class PatientHistoricLocationSyncConsentQRCodeView(generics.GenericAPIView):
    def get(self, request):
        """
        For returning the URL for QR code for obtaining explicit consent from a patient and retrieving the historic locations

        :param request:
        :return:
        """
        return Response({"qr_code_url": settings.HISTORIC_LOCATION_SYNC_CONSENT_QR_CODE_URL})
