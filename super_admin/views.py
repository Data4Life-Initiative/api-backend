from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from authentication.models import Region, DataEntryAdmin, DataEntryAdminRegion, Citizen
from authentication.permissions import IsCitizen, IsDataEntryAdmin, IsSuperUser
from core.models import AreaSeverityLevel, RiskAssessmentRecommendation, SelfScreeningQuestion, WellnessStatusOutcome, \
    MobileNumberWhitelist
from super_admin.serializers import AreaSeverityLevelSerializer, DataEntryAdminSerializerWithPassword, \
    DataEntryAdminSerializerWithoutPassword, RegionSerializer, RiskAssessmentRecommendationSerializer, \
    SelfScreeningQuestionSerializer, WellnessStatusOutcomeSerializer, MobileNumberWhitelistSerializer, \
    SendPushNotificationToCitizenSerializer, SendPushNotificationToAllCitizenSerializer, CitizenListingSerializer


class RegionCRUDViewSet(viewsets.ModelViewSet):
    """
    Defines API for performing CRUD operation on regions

    A region defines a boundary for data entry admins to operate on.
    """
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    permission_classes = (IsAuthenticated, IsSuperUser,)


class DataEntryAdminCRUDViewSet(viewsets.ViewSet):
    """
    Defines API for performing CRUD operation on data entry admins
    """
    serializer_class = DataEntryAdminSerializerWithoutPassword
    permission_classes = (IsAuthenticated, IsSuperUser,)

    def get_serializer_class(self):
        """
        Updates the serializer according to the action being performed on data entry admin

        :return:
        """
        serializer_class = self.serializer_class
        if self.action == "create":
            serializer_class = DataEntryAdminSerializerWithPassword
        return serializer_class

    def create(self, request):
        """
        Creates data entry admin

        :param request:
        :return:
        """
        serializer = self.get_serializer_class()(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request):
        """
        Lists all data entry admin records

        :param request:
        :return:
        """
        queryset = DataEntryAdmin.objects.all()
        serializer = self.get_serializer_class()(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        Retrieves a data entry admin by ID

        :param request:
        :param pk:
        :return:
        """
        queryset = DataEntryAdmin.objects.all()
        data_entry_admin = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer_class()(data_entry_admin)

        return Response(serializer.data)

    def destroy(self, request, pk=None):
        """
        Delete a data entry admin

        :param request:
        :param pk:
        :return:
        """
        queryset = DataEntryAdmin.objects.all()
        data_entry_admin = get_object_or_404(queryset, pk=pk)
        data_entry_admin.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    def update(self, request, pk=None):
        """
        Updates a data entry admin

        :param request:
        :param pk:
        :return:
        """
        queryset = DataEntryAdmin.objects.all()
        data_entry_admin = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer_class()(data_entry_admin, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)


class DataEntryAdminRegionViewSet(viewsets.ViewSet):
    """
    Define API to assign / remove region for a data entry admin
    """
    serializer_class = DataEntryAdminSerializerWithoutPassword
    permission_classes = (IsAuthenticated, IsSuperUser,)

    def create(self, request, pk=None, region_id=None):
        """
        Assigns a region to data entry admin

        :param request:
        :param pk:
        :param region_id:
        :return:
        """
        data_entry_admin_query_set = DataEntryAdmin.objects.all()
        data_entry_admin = get_object_or_404(data_entry_admin_query_set, pk=pk)

        queryset = Region.objects.all()
        region = get_object_or_404(queryset, pk=region_id)

        try:
            DataEntryAdminRegion.objects.get(data_entry_admin__id=data_entry_admin.id,
                                             region__id=region.id)
        except DataEntryAdminRegion.DoesNotExist:
            DataEntryAdminRegion.objects.create(data_entry_admin=data_entry_admin,
                                                region=region)

        serializer = self.serializer_class(data_entry_admin)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk=None, region_id=None):
        """
        Removes a region from data entry admin

        :param request:
        :param pk:
        :param region_id:
        :return:
        """
        data_entry_admin_query_set = DataEntryAdmin.objects.all()
        data_entry_admin = get_object_or_404(data_entry_admin_query_set, pk=pk)

        queryset = Region.objects.all()
        region = get_object_or_404(queryset, pk=region_id)

        try:
            data_entry_admin_region = DataEntryAdminRegion.objects.get(data_entry_admin__id=data_entry_admin.id,
                                                                       region__id=region.id)
            data_entry_admin_region.delete()

            serializer = self.serializer_class(data_entry_admin)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except DataEntryAdminRegion.DoesNotExist:
            response_msg = "Please provide a valid region/data entry admin ID!"
            response_status = status.HTTP_404_NOT_FOUND

            return Response({"msg": response_msg}, status=response_status)


class AreaSeverityLevelCRUDViewSet(viewsets.ViewSet):
    """
    AreaSeverityLevelCRUDViewSet

    ViewSet defining actions for managing severity levels in a region.

    Data entry admin is only allowed update, list, retrieve a severity level.
    Super admin is allowed perform all the CRUD operations on severity level model.
    """
    serializer_class = AreaSeverityLevelSerializer
    permission_classes = (IsAuthenticated, IsSuperUser)

    def get_permissions(self):
        """
        Updates the permission levels required for manipulating area severity levels

        Update, list, retrieve operations are permitted for both data entry admin and super admin as well

        :return:
        """

        # Todo : If the authorized user is data entry admin,
        #  add a check if the region is assigned to data entry admin as well

        permission_classes = self.permission_classes
        if self.action in ('update', 'list', 'retrieve'):
            permission_classes = (
                IsAuthenticated, IsSuperUser | IsDataEntryAdmin,)
        return [permission() for permission in permission_classes]

    def create(self, request, region_pk=None):
        """
        For creating a area severity level for a region

        :param request:
        :param region_pk:
        :return:
        """
        queryset = Region.objects.all()
        region = get_object_or_404(queryset, pk=region_pk)

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(region=region)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request, region_pk=None):
        """
        For listing all the severity levels associated with a region

        :param request:
        :param region_pk:
        :return:
        """
        queryset = Region.objects.all()
        region = get_object_or_404(queryset, pk=region_pk)

        area_severity_level_queryset = AreaSeverityLevel.objects.filter(
            region__id=region.id)
        serializer = self.serializer_class(
            area_severity_level_queryset, many=True)

        return Response(serializer.data)

    def update(self, request, region_pk=None, pk=None):
        """
        For updating the severity level for a region

        :param request:
        :param region_pk:
        :param pk:
        :return:
        """
        queryset = AreaSeverityLevel.objects.all()
        area_severity_level = get_object_or_404(
            queryset, Q(region__id=region_pk), pk=pk)

        serializer = self.serializer_class(
            area_severity_level, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    def retrieve(self, request, region_pk=None, pk=None):
        """
        For retrieving the severity level for a region

        :param request:
        :param region_pk:
        :param pk:
        :return:
        """
        queryset = AreaSeverityLevel.objects.all()
        area_severity_level = get_object_or_404(
            queryset, Q(region__id=region_pk), pk=pk)

        serializer = self.serializer_class(area_severity_level)

        return Response(serializer.data)

    def destroy(self, request, region_pk=None, pk=None):
        """
        For deleting the severity level for a region

        :param request:
        :param region_pk:
        :param pk:
        :return:
        """
        queryset = AreaSeverityLevel.objects.all()
        area_severity_level = get_object_or_404(
            queryset, Q(region__id=region_pk), pk=pk)
        area_severity_level.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class RiskAssessmentRecommendationCRUDViewSet(viewsets.ModelViewSet):
    """
    RiskAssessmentRecommendationCRUDViewSet

    ViewSet defining CRUD actions for risk assessment recommendations

    List action is also accessible by citizen access tokens
    """
    queryset = RiskAssessmentRecommendation.objects.all()
    serializer_class = RiskAssessmentRecommendationSerializer
    permission_classes = (IsAuthenticated, IsSuperUser)

    def get_permissions(self):
        """
        Updates the permission levels required for manipulating risk assessment recommendations

        List operation is permitted for citizen as well

        :return:
        """
        permission_classes = self.permission_classes

        # providing access to citizen access tokens for listing recommendations
        if self.action in ('list',):
            permission_classes = (IsAuthenticated, IsSuperUser | IsCitizen,)
        return [permission() for permission in permission_classes]


class SelfScreeningQuestionCRUDViewSet(viewsets.ModelViewSet):
    """
    SelfScreeningQuestionCRUDViewSet

    ViewSet defining CRUD actions for self screening questions

    List action is also accessible for citizen access tokens
    """
    queryset = SelfScreeningQuestion.objects.all()
    serializer_class = SelfScreeningQuestionSerializer
    permission_classes = (IsAuthenticated, IsSuperUser)

    def get_permissions(self):
        """
        Updates the permission levels required for manipulating self screening questions

        List operation is permitted for citizen as well

        :return:
        """
        permission_classes = self.permission_classes

        # providing access to citizen access tokens for listing questions
        if self.action in ('list',):
            permission_classes = (IsAuthenticated, IsSuperUser | IsCitizen,)
        return [permission() for permission in permission_classes]


class WellnessStatusOutcomeCRUDViewSet(viewsets.ModelViewSet):
    """
    WellnessStatusOutcomeCRUDViewSet

    ViewSet defining CRUD actions for wellness status outcomes

    List action is also accessible for citizen access tokens
    """
    queryset = WellnessStatusOutcome.objects.all()
    serializer_class = WellnessStatusOutcomeSerializer
    permission_classes = (IsAuthenticated, IsSuperUser)

    def get_permissions(self):
        """
        Updates the permission levels required for manipulating wellness status / self screening outcomes

        List operation is permitted for citizen as well

        :return:
        """
        permission_classes = self.permission_classes

        # providing access to citizen access tokens for listing wellness status outcome
        if self.action in ('list',):
            permission_classes = (IsAuthenticated, IsSuperUser | IsCitizen,)
        return [permission() for permission in permission_classes]


class MobileNumberWhitelistCRUDViewSet(viewsets.ModelViewSet):
    """
    Defines API to perform CRUD operations on whitelist for citizen mobile number

    Only the whitelisted mobile numbers are allowed to authenticate to citizen APP using one time password

    This restriction is to control the rate of traffic towards twilio API
    """
    queryset = MobileNumberWhitelist.objects.all()
    serializer_class = MobileNumberWhitelistSerializer
    permission_classes = (IsAuthenticated, IsSuperUser)


class SendPushNotificationToCitizenAPIView(generics.GenericAPIView):
    """
    Defines API to send push notifications to a citizen
    """
    serializer_class = SendPushNotificationToCitizenSerializer
    permission_classes = (IsAuthenticated, IsSuperUser)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data)


class SendPushNotificationToAllCitizenAPIView(generics.GenericAPIView):
    """
    Defines API to send push notifications to all citizens
    """
    serializer_class = SendPushNotificationToAllCitizenSerializer
    permission_classes = (IsAuthenticated, IsSuperUser)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data)


class CitizenListingAPIView(generics.GenericAPIView):
    """
    Listing all citizens
    """
    serializer_class = CitizenListingSerializer
    permission_classes = (IsAuthenticated, IsSuperUser)

    def get(self, request):
        queryset = Citizen.objects.all()
        serializer = self.serializer_class(queryset)

        return Response(serializer.data)
