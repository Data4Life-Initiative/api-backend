from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from authentication.permissions import IsDataEntryAdmin
from core.models import DiseaseInfectionStatus, PatientHistoricLocation
from patient.serializers import PatientHistoricLocationBulkSerializer, PatientHistoricLocationSerializer


class PatientHistoricLocationViewSet(viewsets.ViewSet):
    """
    Defines API to perform CRUD operations on patient historic locations
    """
    serializer_class = PatientHistoricLocationSerializer
    permission_classes = (IsAuthenticated, IsDataEntryAdmin,)

    def get_serializer_class(self):
        """
        Updates the serializer according to the action being performed on patient historic locations

        :return:
        """
        serializer_class = self.serializer_class
        if self.action == "create":
            serializer_class = PatientHistoricLocationBulkSerializer
        return serializer_class

    def list(self, request):
        """
        List all the patient historic locations

        :param request:
        :return:
        """
        queryset = PatientHistoricLocation.objects.all()
        serializer = self.get_serializer_class()(queryset, many=True)

        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        Retrieve a patient historic location

        :param request:
        :param pk:
        :return:
        """
        queryset = PatientHistoricLocation.objects.all()
        historic_location = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer_class()(historic_location)

        return Response(serializer.data)

    def create(self, request):
        """
        Create patient historic location record and add it to database

        :param request:
        :return:
        """

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
        """
        Delete patient historic location

        :param request:
        :param pk:
        :return:
        """
        queryset = PatientHistoricLocation.objects.all()
        historic_location = get_object_or_404(queryset, pk=pk)
        historic_location.delete()

        return Response({}, status=status.HTTP_204_NO_CONTENT)

    def update(self, request, pk=None):
        """
        Update patient historic locations

        :param request:
        :param pk:
        :return:
        """
        queryset = PatientHistoricLocation.objects.all()
        historic_location = get_object_or_404(queryset, pk=pk)

        serializer = self.get_serializer_class()(historic_location, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
