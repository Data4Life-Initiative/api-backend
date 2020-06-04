from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed

from authentication.utils import decode_jwt_token
from authentication.models import Citizen


class KeycloakAuthentication(authentication.BaseAuthentication):
    """
    KeycloakAuthentication

    Custom authentication class for Data4Life backend

    Citizen authentication is partially taken care by keycloak IAM microservice.
    This custom authentication class facilitates the decoding the access tokens issued by keycloak
    and retrieving the associated user object.
    """

    def authenticate(self, request):
        # Fetching the authorization header
        header = request.META.get('HTTP_AUTHORIZATION')
        if header is None:
            return None

        # Fetching raw token data from Bearer {token}
        raw_token = self.get_raw_token(header)

        # Trying to decode the access token.
        # Since keycloak issued token are based on RS256 algorithm,
        # decoding is done using RSA public key
        decoded_token_data = decode_jwt_token(raw_token)

        if not decoded_token_data:
            return None

        # if sub attribute is not present in decoded token then fail
        if 'sub' not in decoded_token_data:
            return None

        return (self.get_user(decoded_token_data['sub']), decoded_token_data)

    def get_raw_token(self, header):
        """
        Extracts an unvalidated JSON web token from the given "Authorization"
        header value.
        """
        parts = header.split()

        if len(parts) == 0:
            # Empty AUTHORIZATION header sent
            return None

        if parts[0] != "Bearer":
            # Assume the header does not contain a JSON web token
            return None

        if len(parts) != 2:
            raise AuthenticationFailed(
                _('Authorization header must contain two space-delimited values'),
                code='bad_authorization_header',
            )

        return parts[1]

    def get_user(self, validated_token_subject):
        """
        Attempts to find and return a user using the given validated token.
        """

        try:
            # Check if the a matching citizen object exists !
            citizen = Citizen.objects.get(iam_user_id__exact=validated_token_subject)
        except Citizen.DoesNotExist:
            raise AuthenticationFailed('User not found', code='user_not_found')

        user = citizen.user

        if not user.is_active:
            raise AuthenticationFailed('User is inactive', code='user_inactive')

        return user
