from rest_framework import status, generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.serializers import TokenRefreshSerializer

from .renderers import UserJSONRenderer
from .serializers import *
from .utils import iam_refresh_user_token


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


class CitizenLoginUsingEmailAPIView(generics.GenericAPIView):
    """
    API to login as citizen via email
    """
    permission_classes = (AllowAny,)
    serializer_class = CitizenLoginUsingEmailSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class CitizenRegistrationAPIView(generics.GenericAPIView):
    """
    Registering a citizen account
    """
    permission_classes = (AllowAny,)
    serializer_class = CitizenRegistrationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class CitizenSendOTPAPIView(generics.GenericAPIView):
    """
    API to login via one time password send to mobile number
    """
    permission_classes = (AllowAny,)
    serializer_class = CitizenSendOTPSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class CitizenVerifyOTPAPIView(generics.GenericAPIView):
    """
    API to verify the one time password and authenticate as citizen
    """
    permission_classes = (AllowAny,)
    serializer_class = CitizenVerifyOTPSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class RefreshTokenAPIView(generics.GenericAPIView):
    """
    Custom refresh token API for supporting refresh tokens issued by both keycloak IAM and simplejwt package
    """
    serializer_class = TokenRefreshSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        # Checking if the refresh token is issued by IAM
        resp_status_code, resp_text = iam_refresh_user_token(request.data.get("refresh", ""),
                                                             iam_client_id="data4life")

        if resp_status_code != 200:
            # Checking if the refresh token is issued by restframework simplejwt package
            try:
                serializer.is_valid(raise_exception=True)
            except TokenError as e:
                raise InvalidToken(e.args[0])

            return Response(serializer.validated_data, status=status.HTTP_200_OK)

        # IAM refresh token response to json
        resp_json = json.loads(resp_text)

        # constructing response similar to that of restframework simplejwt refresh token response
        response = {
            "access": resp_json.get("access_token", ""),
            "refresh": resp_json.get("refresh_token", "")
        }

        return Response(response, status=status.HTTP_200_OK)

# Todo : DataEntryAdmin forgot password (Not important)
# Todo : Token invalidation flow (or blacklisting)
# Todo : Forgot password API
# Todo : Reset password API
