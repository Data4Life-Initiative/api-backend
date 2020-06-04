from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from authentication.permissions import IsCitizen, IsDataEntryAdmin, IsSuperUser
from core.models import Disease, DiseaseInfectionStatus
from disease.serializers import DiseaseSerializer, DiseaseInfectionStatusDetailSerializer, \
    DiseaseInfectionStatusListSerializer


class DiseaseCRUDViewSet(viewsets.ViewSet):
    serializer_class = DiseaseSerializer
    permission_classes = (IsAuthenticated, IsSuperUser,)

    def get_permissions(self):
        permission_classes = self.permission_classes
        if self.action == "list":
            permission_classes = (AllowAny,)
        return [permission() for permission in permission_classes]

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request):
        queryset = Disease.objects.all()
        serializer = self.serializer_class(queryset, many=True)

        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = Disease.objects.all()
        disease = get_object_or_404(queryset, pk=pk)
        serializer = self.serializer_class(disease)

        return Response(serializer.data)

    def update(self, request, pk=None):
        queryset = Disease.objects.all()
        disease = get_object_or_404(queryset, pk=pk)
        serializer = self.serializer_class(disease, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    def destroy(self, request, pk=None):
        queryset = Disease.objects.all()
        disease = get_object_or_404(queryset, pk=pk)
        disease.delete()

        return Response({}, status=status.HTTP_204_NO_CONTENT)


class DiseaseInfectionStatusCRUDViewSet(viewsets.ViewSet):
    serializer_class = DiseaseInfectionStatusDetailSerializer
    permission_classes = (IsAuthenticated, IsSuperUser,)

    def get_permissions(self):
        permission_classes = self.permission_classes
        if self.action == "list":
            permission_classes = (
                IsAuthenticated, IsSuperUser | IsDataEntryAdmin,)
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        serializer_class = self.serializer_class
        if self.action == "list":
            serializer_class = DiseaseInfectionStatusListSerializer
        return serializer_class

    def create(self, request, disease_pk=None):
        queryset = Disease.objects.all()
        disease = get_object_or_404(queryset, pk=disease_pk)

        serializer = self.get_serializer_class()(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(disease=disease)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request, disease_pk=None):
        queryset = Disease.objects.all()
        disease = get_object_or_404(queryset, pk=disease_pk)

        disease_infection_status_set = DiseaseInfectionStatus.objects.filter(
            disease=disease)

        serializer = self.get_serializer_class()(
            disease_infection_status_set, many=True)

        return Response(serializer.data)

    def retrieve(self, request, disease_pk=None, pk=None):
        try:
            disease_infection_status = DiseaseInfectionStatus.objects.get(
                disease__id=disease_pk, id=pk)

            serializer = self.get_serializer_class()(disease_infection_status)

            return Response(serializer.data)

        except DiseaseInfectionStatus.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def update(self, request, disease_pk=None, pk=None):
        try:
            disease_infection_status = DiseaseInfectionStatus.objects.get(
                disease__id=disease_pk, id=pk)

            serializer = self.get_serializer_class()(
                disease_infection_status, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data)

        except DiseaseInfectionStatus.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, disease_pk=None, pk=None):
        try:
            disease_infection_status = DiseaseInfectionStatus.objects.get(
                disease__id=disease_pk, id=pk)
            disease_infection_status.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        except DiseaseInfectionStatus.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
