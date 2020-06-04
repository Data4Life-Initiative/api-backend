from rest_framework import status, generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .renderers import UserJSONRenderer
from .serializers import DataEntryAdminLoginSerializer, CitizenSendOTPSerializer, \
    CitizenVerifyOTPSerializer, SuperAdminLoginSerializer, CitizenRegistrationSerializer, \
    CitizenLoginUsingEmailSerializer


class SuperAdminLoginAPIView(generics.GenericAPIView):
    """
    API to login as super admin
    """
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = SuperAdminLoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class DataEntryAdminLoginAPIView(generics.GenericAPIView):
    """
    API to login as data entry admin
    """
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = DataEntryAdminLoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


# Todo : DataEntryAdmin forgot password (Not important)
# Todo : Token invalidation flow (or blacklisting)

class CitizenLoginUsingEmailAPIView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = CitizenLoginUsingEmailSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class CitizenRegistrationAPIView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = CitizenRegistrationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class CitizenSendOTPAPIView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = CitizenSendOTPSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class CitizenVerifyOTPAPIView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = CitizenVerifyOTPSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

# Todo : Push notification device registration API
# Todo : Citizen logout API
# Todo : Triggering profile update in keycloak IAM, while profile gets updated in django
# Todo : Citizen forgot password API
# Todo : Reset password API
# Todo : Refresh token flow, integrate it with existing refresh token flow provided by simplejwt
