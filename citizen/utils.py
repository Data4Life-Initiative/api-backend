# Reference - https://github.com/jitendrapurbey/qr_api/blob/master/api/utils.py

import base64
import io
import json
from datetime import date, timedelta

import qrcode
# e.g. calculateAge(date(1997, 2, 3))
from django.conf import settings
from django.utils import timezone
from haversine import haversine, Unit

from authentication.models import FCMPushNotificationRegistrationToken
from authentication.utils import iam_update_user_info, iam_get_user_token
from core.models import PatientHistoricLocation, CitizenPushNotifications


def calculateAge(dob):
    """
    Calculates the age using date of birth

    :param dob:
    :return:
    """
    dob = date(dob.split("-")[0], dob.split("-")[1], dob.split("-")[2])
    today = date.today()
    try:
        birthday = dob.replace(year=today.year)

    # raised when birth date is February 29
    # and the current year is not a leap year
    except ValueError:
        birthday = dob.replace(year=today.year,
                               month=dob.month + 1, day=1)

    if birthday > today:
        return today.year - dob.year - 1
    else:
        return today.year - dob.year


def generate_qr_code(data, size=10, border=0):
    """
    Generates QR code image with payload data embedded

    :param data:
    :param size:
    :param border:
    :return:
    """
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=size, border=border)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image()
    return img


def generate_qr(payload):
    """
    Generate the QR code and returns the base64 of image

    :param payload:
    :return:
    """
    generated_code = generate_qr_code(data=payload, size=4, border=1)
    bio = io.BytesIO()
    img_save = generated_code.save(bio)
    png_qr = bio.getvalue()
    base64qr = base64.b64encode(png_qr)
    img_base64_data = base64qr.decode("utf-8")
    context_dict = dict()
    context_dict['file_type'] = "png"
    context_dict['image_base64'] = img_base64_data
    return context_dict


def update_citizen_user_info_to_iam(citizen_disease_relation_instance):
    """
    Reflecting the updates to citizen profile to the corresponding user info in keycloak IAM

    This function will be executed in a background thread, to have non-blocking experience while updating user profile

    :param citizen_disease_relation_instance:
    :return:
    """

    # getting IAM admin access token
    status_code, response_text = iam_get_user_token(username=settings.IAM_ADMIN_USERNAME,
                                                    password=settings.IAM_ADMIN_PASSWORD, client_id="admin-cli",
                                                    realm="master")

    if status_code != 200:
        settings.LOGGER_ERROR.error("Failed to update citizen profile - Reason: Failed to get IAM access token")
        return False

    response_json = json.loads(response_text)

    if 'access_token' not in response_json:
        settings.LOGGER_ERROR.error("Failed to update citizen profile - Reason: Failed to get IAM access token")
        return False

    iam_admin_access_token = response_json['access_token']

    # updating the full name in the IAM
    status_code, response_text = iam_update_user_info(fullname=citizen_disease_relation_instance.citizen.fullname,
                                                      iam_user_id=citizen_disease_relation_instance.citizen.iam_user_id,
                                                      admin_access_token=iam_admin_access_token)
    if status_code != 200:
        settings.LOGGER_ERROR.error("Failed to update citizen profile in IAM")
        return False

    return True


def send_hotspot_proximity_notifications(citizen_location_lat, citizen_location_long, citizen_obj):
    """
    Function that check if the provided citizen location coordinates is in proximity with patient historic locations
    if it is within proximity, then send hotspot proximity notifications

    This function is to executed thread for non blocking experience

    :param citizen_location_lat:
    :param citizen_location_long:
    :param citizen_obj:
    :return:
    """
    try:

        # fetching all non expired patient historic locations
        patient_historic_locations = PatientHistoricLocation.objects.filter(
            recorded_date_time__gte=timezone.now() - timedelta(
                seconds=settings.HISTORIC_LOCATION_EXPIRY_IN_SECONDS)).order_by('-recorded_date_time')

        # looping through patient historic locations to find if anything is in proximity with citizen location
        for patient_historic_location in patient_historic_locations:
            historic_location_coords = (patient_historic_location.lat, patient_historic_location.long)
            citizen_location_coords = (citizen_location_lat, citizen_location_long)

            # Check if the distance within proximity
            distance = haversine(citizen_location_coords, historic_location_coords, unit=Unit.METERS)
            if distance <= settings.HOTSPOT_PROXIMITY_IN_METRES:
                # check the delay between last notification send to this citizen
                citizen_notifications_set = CitizenPushNotifications.objects.filter(citizen=citizen_obj).order_by(
                    '-added_on')

                is_send_notification = False

                if citizen_notifications_set.count() == 0:
                    is_send_notification = True
                else:
                    # calculate the delay in seconds between last notification and current time
                    last_notification = citizen_notifications_set[0]
                    seconds_elapsed_since_last_notification = (timezone.now() - last_notification.added_on).seconds

                    if seconds_elapsed_since_last_notification > settings.DELAY_BETWEEN_NOTIFICATIONS_IN_SECONDS:
                        is_send_notification = True

                if is_send_notification:
                    # send hotspot proximity notifications
                    citizen_device_query_set = FCMPushNotificationRegistrationToken.objects.filter(
                        user=citizen_obj.user)
                    citizen_device_query_set.send_message(None, extra={
                        "notification": {
                            "title": "Hotspot proximity warning !",
                            "body": "There are disease hotspots nearby your location !"
                        },
                        "data": {
                            "type": "HOTSPOT-PROXIMITY"
                        }
                    })

                    return None

        return None

    except:
        settings.LOGGER_ERROR.error(
            "Something went wrong while trying to send proximity notifications to citizen:{}",
            citizen_obj.mobile_number)
