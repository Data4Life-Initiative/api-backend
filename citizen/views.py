import base64
import json

from django.conf import settings
from django.db.models import Q
from django.http import HttpResponse
from rest_framework import generics, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from authentication.models import Citizen
from authentication.permissions import IsCitizen
from citizen.serializers import CitizenLocationSyncSerializer, CitizenSerializer, QRSerializer
from citizen.utils import generate_qr
from core.models import CitizenDiseaseRelation, Disease, PatientHistoricLocation
from dashboard.serializers import MapDataSerializer
from patient.serializers import HistoricLocationDataSerializer


class CitizenMapDataAPIView(generics.GenericAPIView):
    """
    CitizenMapDataAPIView

    API for retrieving the disease hotspot data for homepage map
    """
    serializer_class = HistoricLocationDataSerializer
    permission_classes = (IsAuthenticated, IsCitizen)

    def get(self, request):
        historic_locations = PatientHistoricLocation.objects.all()
        serializer = self.serializer_class(historic_locations, many=True)

        return Response(serializer.data)


class CitizenProfileAPIView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated, IsCitizen)
    serializer_class = CitizenSerializer

    def get(self, request, *args, **kwargs):
        """
        For retrieving the citizen profile data
        """

        try:
            disease = Disease.objects.get(name="COVID-19")
        except Disease.DoesNotExist as e:
            settings.LOGGER_ERROR.error(str(e))

            return Response({"msg": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            citizen_disease_relation = CitizenDiseaseRelation.objects.get(
                citizen__user=request.user, disease=disease)
        except CitizenDiseaseRelation.DoesNotExist as e:
            settings.LOGGER_ERROR.error(str(e))

            return Response({"msg": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        serializer = self.serializer_class(citizen_disease_relation)

        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        """
        For updating the citizen profile data
        """
        try:
            disease = Disease.objects.get(name="COVID-19")
        except Disease.DoesNotExist as e:
            settings.LOGGER_ERROR.error(str(e))

            return Response({"msg": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            citizen_disease_relation = CitizenDiseaseRelation.objects.get(
                citizen__user=request.user, disease=disease)
        except CitizenDiseaseRelation.DoesNotExist as e:
            settings.LOGGER_ERROR.error(str(e))

            return Response({"msg": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        serializer = self.serializer_class(
            citizen_disease_relation, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)


class CitizenQRCodeAPIView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated, IsCitizen)

    def get(self, request):
        output = generate_qr(json.dumps(
            {"id": str(Citizen.objects.get(user__id=request.user.id).id)}))
        result = QRSerializer(output).data

        # custom response for serving QR code
        response = HttpResponse(content_type="image/png")
        response.write(base64.b64decode(result['image_base64'].encode()))
        return response


class CitizenLocationSyncAPIView(generics.GenericAPIView):
    serializer_class = CitizenLocationSyncSerializer
    permission_classes = (IsAuthenticated, IsCitizen)

    def post(self, request):
        citizen = Citizen.objects.get(user__id=request.user.id)

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(citizen=citizen)

        return Response(status=status.HTTP_200_OK)


# Todo : Perform risk assessment
# Todo : Noitifications
