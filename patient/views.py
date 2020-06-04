from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from authentication.permissions import IsDataEntryAdmin
from core.models import Disease, DiseaseInfectionStatus, PatientHistoricLocation
from patient.serializers import PatientHistoricLocationBulkSerializer, PatientHistoricLocationSerializer


class PatientHistoricLocationViewSet(viewsets.ViewSet):
    serializer_class = PatientHistoricLocationSerializer
    permission_classes = (IsAuthenticated, IsDataEntryAdmin,)

    def get_serializer_class(self):
        serializer_class = self.serializer_class
        if self.action == "create":
            serializer_class = PatientHistoricLocationBulkSerializer
        return serializer_class

    def list(self, request):
        queryset = PatientHistoricLocation.objects.all()
        serializer = self.get_serializer_class()(queryset, many=True)

        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = PatientHistoricLocation.objects.all()
        historic_location = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer_class()(historic_location)

        return Response(serializer.data)

    def create(self, request):

        # for validating the request payload structure
        validation_serializer = self.get_serializer_class()(data=request.data)
        validation_serializer.is_valid(raise_exception=True)

        # retrieving the infection status object
        infection_status = DiseaseInfectionStatus.objects.get(
            id=request.data.get('infection_status_id'))

        # creating bulk patient historic location objects
        create_serializer = PatientHistoricLocationSerializer(
            data=request.data.get('historic_locations'), many=True)
        create_serializer.is_valid(raise_exception=True)
        create_serializer.save(infection_status=infection_status)

        return Response(validation_serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk=None):
        queryset = PatientHistoricLocation.objects.all()
        historic_location = get_object_or_404(queryset, pk=pk)
        historic_location.delete()

        return Response({}, status=status.HTTP_204_NO_CONTENT)

    def update(self, request, pk=None):
        queryset = PatientHistoricLocation.objects.all()
        historic_location = get_object_or_404(queryset, pk=pk)

        serializer = self.get_serializer_class()(historic_location, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
