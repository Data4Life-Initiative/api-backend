import datetime
import json

import phonenumbers
import twilio.rest
from django.conf import settings
from django.contrib.auth import authenticate
from phonenumbers import NumberParseException
from rest_framework import serializers
from twilio.base.exceptions import TwilioRestException

from core.models import CitizenDiseaseRelation, Disease, MobileNumberWhitelist
from super_admin.serializers import RegionSerializer
from .models import User, DataEntryAdmin, Citizen, DataEntryAdminRegion
from .utils import iam_register_user, iam_get_user_token, iam_search_user_by_email


class TokenSerializer(serializers.Serializer):
    """
    Serializes user token data (access, refresh pair)
    """
    access = serializers.CharField()
    refresh = serializers.CharField()


class DataEntryAdminLoginSerializer(serializers.Serializer):
    """
    DataEntryAdminLoginSerializer

    Serializers data entry admin login requests, returns token and basic profile data.
    """
    email = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=128, write_only=True)
    token = TokenSerializer(read_only=True)

    fullname = serializers.CharField(read_only=True)
    designation = serializers.CharField(read_only=True)
    department = serializers.CharField(read_only=True)
    organisation = serializers.CharField(read_only=True)
    regions = RegionSerializer(many=True, read_only=True)
    mobile_number = serializers.CharField(read_only=True)

    def validate(self, data):
        email = data.get('email', None)
        password = data.get('password', None)

        if email is None:
            raise serializers.ValidationError(
                'An email address is required to log in.'
            )

        if password is None:
            raise serializers.ValidationError(
                'A password is required to log in.'
            )

        user = authenticate(username=email, password=password)

        if user is None:
            raise serializers.ValidationError(
                'A user with this email and password was not found.'
            )

        if not user.is_active:
            raise serializers.ValidationError(
                'This user has been deactivated.'
            )

        try:
            data_entry_admin = DataEntryAdmin.objects.get(user=user)
        except DataEntryAdmin.DoesNotExist as e:
            raise serializers.ValidationError(
                'A user with this email and password was not found.'
            )

        data_entry_admin_regions_queryset = DataEntryAdminRegion.objects.filter(
            data_entry_admin__id=data_entry_admin.id)
        data_entry_admin_region_set = [RegionSerializer(data_entry_admin_region.region).data for data_entry_admin_region
                                       in
                                       data_entry_admin_regions_queryset]

        return {
            "id": user.id,
            "email": user.email,
            "mobile_number": data_entry_admin.mobile_number,
            "fullname": data_entry_admin.fullname,
            "designation": data_entry_admin.designation,
            "department": data_entry_admin.department,
            "organisation": data_entry_admin.organisation,
            "regions": data_entry_admin_region_set,
            "token": user.token
        }


class CitizenLoginUsingEmailSerializer(serializers.Serializer):
    """
    CitizenLoginUsingEmailSerializer

    Serializes citizen login via email,password data
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    # citizen id
    id = serializers.CharField(read_only=True)
    mobile_number = serializers.CharField(read_only=True)
    fullname = serializers.CharField(read_only=True)
    dob = serializers.CharField(read_only=True)
    home_latitude = serializers.FloatField(default=0.0, read_only=True)
    home_longitude = serializers.FloatField(default=0.0, read_only=True)
    wellness = serializers.CharField(read_only=True)
    is_location_sync_enabled = serializers.BooleanField(read_only=True)

    token = TokenSerializer(read_only=True)

    def validate(self, data):

        try:
            disease = Disease.objects.get(name="COVID-19")
        except Disease.DoesNotExist as e:
            raise serializers.ValidationError('Unable to fetch diseases. Initialize disease db')

        email = data.get('email')
        password = data.get('password')

        if User.objects.filter(email=email).count() == 0:
            raise serializers.ValidationError('Please provide valid credentials !')

        # getting associated user object
        user = User.objects.get(email=email)

        try:
            # getting associated citizen object
            citizen = Citizen.objects.get(user=user)
            citizen_disease_relation = CitizenDiseaseRelation.objects.get(citizen=citizen, disease=disease)
        except (Citizen.DoesNotExist, CitizenDiseaseRelation.DoesNotExist):
            raise serializers.ValidationError('Please provide valid credentials !')

        # authenticating in IAM backend
        # getting the refresh, access token pair from the IAM
        status_code, response_text = iam_get_user_token(username=email, password=password,
                                                        client_id="data4life", realm="data4life")

        if status_code != 200:
            settings.LOGGER_ERROR.error("Failed to login to citizen account - Reason: Unable to login to IAM backend")
            raise serializers.ValidationError("Failed to login to citizen account !")

        # authenticating in django backend
        user = authenticate(username=user.username, password=password)

        if user is None:
            raise serializers.ValidationError(
                'A citizen account with this email and password was not found.'
            )

        if not user.is_active:
            raise serializers.ValidationError(
                'This citizen account has been deactivated.'
            )

        return {
            "id": citizen.id,
            "mobile_number": citizen.mobile_number,
            "email": citizen.user.email,
            "fullname": citizen.fullname,
            "dob": citizen.dob,
            "home_latitude": citizen.home_latitude,
            "home_longitude": citizen.home_longitude,
            "wellness": citizen_disease_relation.wellness,
            "token": {
                "refresh": json.loads(response_text)["refresh_token"],
                "access": json.loads(response_text)["access_token"]
            },
            "is_location_sync_enabled": citizen.is_location_sync_enabled
        }


class CitizenRegistrationSerializer(serializers.Serializer):
    """
    CitizenRegistrationSerializer

    Serializes citizen registration data
    """
    mobile_number = serializers.CharField(min_length=12, max_length=15, write_only=True)
    email = serializers.EmailField(write_only=True)
    fullname = serializers.CharField(min_length=3, max_length=50, write_only=True)
    dob = serializers.CharField(write_only=True)
    password = serializers.CharField(min_length=5, write_only=True, trim_whitespace=True)

    msg = serializers.CharField(read_only=True)

    def validate_dob(self, dob):
        """
        Validates date of birth

        :param dob:
        :return:
        """
        try:
            datetime.datetime.strptime(dob, '%d-%m-%Y')
        except ValueError:
            raise serializers.ValidationError(
                "Incorrect date format, should be dd-mm-yyyy")
        return dob

    def validate_email(self, email):
        """
        Validates whether the given email is already in use or not

        :param email:
        :return:
        """
        if User.objects.filter(email=email).count() > 0:
            raise serializers.ValidationError('Email is already in use !')
        return email

    def validate_mobile_number(self, mobile_number):
        """
        Validates whether the given mobile number is in use or not

        :param mobile_number:
        :return:
        """
        if User.objects.filter(username=mobile_number).count() > 0:
            raise serializers.ValidationError('Mobile number is already in use !')
        return mobile_number

    def create(self, validated_data):
        """
        Adds citizen record to postgresql db and corresponding user in keycloak IAM

        :param validated_data:
        :return:
        """

        mobile_number = validated_data.get('mobile_number')
        email = validated_data.get('email')
        fullname = validated_data.get('fullname')
        dob = validated_data.get('dob')
        password = validated_data.get('password')

        try:

            try:
                disease = Disease.objects.get(name="COVID-19")
            except Disease.DoesNotExist as e:
                raise serializers.ValidationError('Unable to fetch diseases. Initialize disease db')

            # getting IAM admin access token
            status_code, response_text = iam_get_user_token(username=settings.IAM_ADMIN_USERNAME,
                                                            password=settings.IAM_ADMIN_PASSWORD, client_id="admin-cli",
                                                            realm="master")

            if status_code != 200:
                settings.LOGGER_ERROR.error("Failed to create citizen account - Reason: Failed to get IAM access token")
                raise serializers.ValidationError("Something went wrong while creating citizen account !")

            response_json = json.loads(response_text)

            if 'access_token' not in response_json:
                raise serializers.ValidationError("Something went wrong while creating citizen account !")

            iam_admin_access_token = response_json['access_token']

            # creating user in IAM
            status_code, response_text = iam_register_user(fullname=fullname, username=email, email=email,
                                                           password=password,
                                                           admin_access_token=iam_admin_access_token)

            if status_code != 201:
                settings.LOGGER_ERROR.error("Failed to create citizen account - Reason: Failed to create user in IAM")
                raise serializers.ValidationError("Something went wrong while creating citizen account !")

            # get the iam user id
            status_code, response_json = iam_search_user_by_email(email=email,
                                                                  admin_access_token=iam_admin_access_token)

            if status_code != 200:
                settings.LOGGER_ERROR.error(
                    "Failed to create citizen account - Reason: Unable to fetch user by email in IAM")
                raise serializers.ValidationError("Something went wrong while creating citizen account !")

            # creating user object
            user = User.objects.create_user(username=mobile_number, email=email, password=password)

            # creating citizen object
            citizen = Citizen.objects.create(iam_user_id=response_json['id'],
                                             user=user,
                                             mobile_number=mobile_number,
                                             fullname=fullname,
                                             dob=dob)

            # create citizen disease relation object
            CitizenDiseaseRelation.objects.create(disease=disease, citizen=citizen)

            return {"msg": "Registered successfully !"}
        except Exception as e:
            print(str(e))
            raise serializers.ValidationError("Something went wrong while creating citizen account !")


class CitizenSendOTPSerializer(serializers.Serializer):
    """
    Serializes data for citizen login via one time password to corresponding mobile number
    """
    mobile_number = serializers.CharField(min_length=12, max_length=15, write_only=True)
    msg = serializers.CharField(read_only=True)
    hash = serializers.CharField(default="", write_only=True)

    def validate(self, data):
        mobile_number = data.get("mobile_number", None)

        # Checking whether the phone number is valid format or not
        try:
            parsed_mobile_number = phonenumbers.parse(mobile_number, None)
        except NumberParseException:
            raise serializers.ValidationError(
                "{} is not valid, please provide a valid mobile number !".format(mobile_number))

        if not phonenumbers.is_possible_number(parsed_mobile_number):
            raise serializers.ValidationError(
                "{} is not valid, please provide a valid mobile number !".format(mobile_number))

        is_authorized_to_login = False

        # Validating if the given number is authorized to login or not
        whitelisted_mobile_number_queryset = MobileNumberWhitelist.objects.all()
        for whitelisted_mobile_number in whitelisted_mobile_number_queryset:
            if mobile_number.strip() == whitelisted_mobile_number.mobile_number:
                is_authorized_to_login = True
                break

        if not is_authorized_to_login:
            raise serializers.ValidationError(
                'This mobile number is not authorized to login. Please contact the administrator !')

        # Checking if there is a user account associated with the given phone number
        try:
            user = User.objects.get(username=mobile_number)
        except User.DoesNotExist as e:
            raise serializers.ValidationError('Account associated with given mobile number is not found !')

        user.set_otp(length=6)
        user.save()

        random_hash = data.get("hash", "")

        account = settings.TWILIO_ACCOUNT_ID
        token = settings.TWILIO_TOKEN
        client = twilio.rest.Client(account, token)

        try:
            # Sends the SMS with one time password to the given mobile number
            client.messages.create(to=mobile_number, from_=settings.TWILIO_MOBILE_NUMBER,
                                   body=settings.OTP_MESSAGE.format(otp_code=user.raw_otp, random_hash=random_hash))
        except TwilioRestException as e:
            raise serializers.ValidationError("Failed to send SMS to {}".format(mobile_number))

        return {"msg": "SMS send to {}".format(mobile_number)}


class CitizenVerifyOTPSerializer(serializers.Serializer):
    """
    Serializer for verifying the one time password and authenticating the citizen.
    """
    mobile_number = serializers.CharField(min_length=12, max_length=15)
    otp = serializers.CharField(write_only=True, trim_whitespace=True, min_length=6, max_length=6)

    # citizen id
    id = serializers.CharField(read_only=True)
    email = serializers.CharField(read_only=True)
    fullname = serializers.CharField(default="", read_only=True)
    dob = serializers.CharField(read_only=True)
    home_latitude = serializers.FloatField(default=0.0, read_only=True)
    home_longitude = serializers.FloatField(default=0.0, read_only=True)

    wellness = serializers.CharField(read_only=True)
    is_location_sync_enabled = serializers.BooleanField(read_only=True)

    token = TokenSerializer(read_only=True)

    def validate(self, data):

        # temp validation : checks if the database contains a disease record associated with COVID-19
        try:
            disease = Disease.objects.get(name="COVID-19")
        except Disease.DoesNotExist as e:
            raise serializers.ValidationError('Unable to fetch diseases. Initialize disease db')

        mobile_number = data.get("mobile_number", None)
        otp = data.get("otp", None)

        # Checking if there is a user account associated with the given phone number
        try:
            user = User.objects.get(username=mobile_number)
        except User.DoesNotExist as e:
            raise serializers.ValidationError(
                'There is citizen record associated with this {} mobile number'.format(mobile_number)
            )

        # Verifying the provided one time password
        verification_status = user.verify_otp(otp)

        if verification_status is None:
            raise serializers.ValidationError(
                "Invalid OTP !"
            )

        if not verification_status:
            raise serializers.ValidationError(
                "OTP has expired !"
            )

        # invalidate the otp
        user.otp = ""
        user.otp_expiry = None
        user.save()

        try:
            citizen = Citizen.objects.get(user=user)
            citizen_disease_relation = CitizenDiseaseRelation.objects.get(citizen=citizen, disease=disease)
        except Citizen.DoesNotExist as e:

            # create citizen object
            citizen = Citizen.objects.create(user=user, mobile_number=mobile_number)

            # create citizen disease relation object
            citizen_disease_relation = CitizenDiseaseRelation.objects.create(disease=disease, citizen=citizen)

        return {
            "id": citizen.id,
            "mobile_number": citizen.mobile_number,
            "email": citizen.user.email,
            "fullname": citizen.fullname,
            "dob": citizen.dob,
            "home_latitude": citizen.home_latitude,
            "home_longitude": citizen.home_longitude,
            "wellness": citizen_disease_relation.wellness,
            "token": user.token,
            "is_location_sync_enabled": citizen.is_location_sync_enabled
        }


class SuperAdminLoginSerializer(serializers.Serializer):
    """
    SuperAdminLoginSerializer

    Serializers super admin login requests, returns token.
    """
    email = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=128, write_only=True)
    token = TokenSerializer(read_only=True)

    id = serializers.CharField(read_only=True)

    def validate(self, data):
        email = data.get('email', None)
        password = data.get('password', None)

        if email is None:
            raise serializers.ValidationError(
                'An email address is required to log in.'
            )

        if password is None:
            raise serializers.ValidationError(
                'A password is required to log in.'
            )

        # Checking if there is a super user account associated with the email
        if User.objects.filter(username=email, is_superuser=True, is_staff=True).count() == 0:
            settings.LOGGER_ERROR.error("Unable to find superuser with given credentials in db !")
            raise serializers.ValidationError(
                'A superuser with this email and password was not found.'
            )

        user = authenticate(username=email, password=password)

        if user is None:
            settings.LOGGER_ERROR.error("Unable to authenticate superuser !")
            raise serializers.ValidationError(
                'A superuser with this email and password was not found.'
            )

        if not user.is_active:
            raise serializers.ValidationError(
                'This superuser has been deactivated.'
            )

        return {
            "id": user.id,
            "email": user.username,
            "token": user.token
        }
