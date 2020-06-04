import base64
import json
from datetime import timedelta

from django.conf import settings
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import generics, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from authentication.models import Citizen, FCMPushNotificationRegistrationToken
from authentication.permissions import IsCitizen
from citizen.serializers import CitizenSerializer, QRSerializer, \
    PushNotificationDeviceRegistrationTokenSerializer, PushNotificationTokenDeleteSerializer, \
    PushNotificationListingSerializer, CitizenHistoricLocationDiseaseRelationSerializer
from citizen.utils import generate_qr
from core.models import CitizenDiseaseRelation, Disease, PatientHistoricLocation, CitizenPushNotifications, \
    CitizenHistoricLocationDiseaseRelation
from patient.serializers import HistoricLocationDataSerializer


class CitizenMapDataAPIView(generics.GenericAPIView):
    """
    CitizenMapDataAPIView

    API for retrieving the disease hotspot data for homepage map
    """
    serializer_class = HistoricLocationDataSerializer
    permission_classes = (IsAuthenticated, IsCitizen)

    def get(self, request):
        historic_locations = PatientHistoricLocation.objects.filter(recorded_date_time__gte=timezone.now() - timedelta(
            seconds=settings.HISTORIC_LOCATION_EXPIRY_IN_SECONDS)).order_by('-recorded_date_time')
        serializer = self.serializer_class(historic_locations, many=True)

        return Response(serializer.data)


class CitizenProfileAPIView(generics.GenericAPIView):
    """
    Defines API for retrieving and updating citizen profile
    """
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


class CitizenHistoricLocationDiseaseRelationViewSet(viewsets.ModelViewSet):
    """
    Defines CRUD API handling historic locations of a citizen associated with a disease
    """
    queryset = CitizenHistoricLocationDiseaseRelation.objects.all().order_by('-recorded_date_time')
    serializer_class = CitizenHistoricLocationDiseaseRelationSerializer
    permission_classes = (IsAuthenticated, IsCitizen)

    def create(self, request, *args, **kwargs):
        citizen = Citizen.objects.get(user__id=request.user.id)

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(citizen=citizen)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CitizenQRCodeAPIView(generics.GenericAPIView):
    """
    QR code for citizen profile

    Todo : What is the use case of this ??
    """
    permission_classes = (IsAuthenticated, IsCitizen)

    def get(self, request):
        output = generate_qr(json.dumps(
            {"id": str(Citizen.objects.get(user__id=request.user.id).id)}))
        result = QRSerializer(output).data

        # custom response for serving QR code
        response = HttpResponse(content_type="image/png")
        response.write(base64.b64decode(result['image_base64'].encode()))
        return response


class PushNotificationDeviceRegistrationTokenAPIView(generics.GenericAPIView):
    """
    PushNotificationDeviceRegistrationTokenAPIView

    For manipulating push notification registration tokens associated with a user and
    given device_id
    """
    serializer_class = PushNotificationDeviceRegistrationTokenSerializer
    permission_classes = (IsAuthenticated, IsCitizen,)

    def post(self, request):
        """
        For registering the push notification registration token for particular device,
        previous tokens registered for this device is removed in the process.

        :param request:
        :return:
        """

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)

        return Response(status=status.HTTP_201_CREATED)


class PushNotificationDeviceRegistrationTokenDeleteAPIView(generics.GenericAPIView):
    serializer_class = PushNotificationTokenDeleteSerializer
    permission_classes = (IsAuthenticated, IsCitizen,)

    def delete(self, request):
        """
        For deleting all the push notification tokens associated with particular device, this API should be
        called on logout. So that after logout, the device doesn't receive any more push notifications.

        :param request:
        :return:
        """

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        device_id = serializer.data.get('device_id')

        # deleting the push notification token records
        FCMPushNotificationRegistrationToken.objects.filter(user__id=request.user.id, device_id=device_id).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class NotificationsListingAPIView(generics.GenericAPIView):
    """
    NotificationsListingAPIView

    For listing notifications for a citizen

    # Todo : pagination
    """
    serializer_class = PushNotificationListingSerializer
    permission_classes = (IsAuthenticated, IsCitizen,)

    def get(self, request):

        page = request.GET.get('page', 1)

        notifications_query_set = CitizenPushNotifications.objects.filter(citizen__user__id=request.user.id).order_by(
            '-added_on')

        paginator = Paginator(notifications_query_set, 10)
        try:
            notifications_query_set = paginator.page(page)
        except PageNotAnInteger:
            notifications_query_set = paginator.page(1)
        except EmptyPage:
            notifications_query_set = paginator.page(paginator.num_pages)

        serializer = self.serializer_class(notifications_query_set, many=True)

        return Response(serializer.data)


class NotificationReadStatusUpdate(generics.GenericAPIView):
    """
    NotificationReadStatusUpdate

    To mark a notification as read or unread
    """
    permission_classes = (IsAuthenticated, IsCitizen,)

    def post(self, request, pk=None, notification_read_status=None):

        # retrieving the notification from the db
        try:
            notification = CitizenPushNotifications.objects.get(citizen__user__id=request.user.id, id=pk)
        except CitizenPushNotifications.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # checking if it is valid notification status
        if notification_read_status not in ('read', 'unread'):
            return Response(status=status.HTTP_404_NOT_FOUND)

        # marking the notification as read or unread
        if notification_read_status == "read":
            notification.is_read = True
            notification.save()
        else:
            notification.is_read = False
            notification.save()

        return Response(status=status.HTTP_200_OK)


class PerformRiskAssessmentAPI(generics.GenericAPIView):
    """
    Returns a mock score for risk assessment
    """

    permission_classes = (IsAuthenticated, IsCitizen,)

    def get(self, request):
        return Response({"score": 4.3})

# Todo : List notification types
