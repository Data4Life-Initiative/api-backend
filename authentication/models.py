import datetime

from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone
from push_notifications.models import Device, CLOUD_MESSAGE_TYPES, GCMDeviceManager
from push_notifications.settings import PUSH_NOTIFICATIONS_SETTINGS as SETTINGS
from rest_framework_simplejwt.tokens import RefreshToken

from .utils import random_number_generator, hex_uuid


class UserManager(BaseUserManager):

    def create_user(self, username, email, password=None):
        """Create and return a `User` with an email, username and password."""
        if username is None:
            raise TypeError('Users must have a username.')

        if email is None:
            raise TypeError('Users must have an email address.')

        user = self.model(username=username, email=self.normalize_email(email))
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, username, email, password):
        """
        Create and return a `User` with superuser (admin) permissions.
        """
        if password is None:
            raise TypeError('Superusers must have a password.')

        user = self.create_user(username, email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user


class User(AbstractBaseUser, PermissionsMixin):
    id = models.CharField(primary_key=True, default=hex_uuid, editable=False, unique=True, max_length=36)

    # Each `User` needs a human-readable unique identifier that we can use to
    # represent the `User` in the UI. We want to index this column in the
    # database to improve lookup performance.
    username = models.CharField(db_index=True, max_length=255, unique=True)

    # We also need a way to contact the user and a way for the user to identify
    # themselves when logging in. Since we need an email address for contacting
    # the user anyways, we will also use the email for logging in because it is
    # the most common form of login credential at the time of writing.
    email = models.EmailField(blank=True, null=True, default="")

    # When a user no longer wishes to use our platform, they may try to delete
    # their account. That's a problem for us because the data we collect is
    # valuable to us and we don't want to delete it. We
    # will simply offer users a way to deactivate their account instead of
    # letting them delete it. That way they won't show up on the site anymore,
    # but we can still analyze the data.
    is_active = models.BooleanField(default=True)

    # The `is_staff` flag is expected by Django to determine who can and cannot
    # log into the Django admin site. For most users this flag will always be
    # false.
    is_staff = models.BooleanField(default=False)

    # A timestamp representing when this object was created.
    created_at = models.DateTimeField(auto_now_add=True)

    # A timestamp reprensenting when this object was last updated.
    updated_at = models.DateTimeField(auto_now=True)

    # sms based auth fields
    otp = models.CharField(max_length=500, blank=True, null=True)
    otp_expiry = models.DateTimeField(blank=True, null=True, default=None)

    # The `USERNAME_FIELD` property tells us which field we will use to log in.
    # In this case we want it to be the email field.
    USERNAME_FIELD = 'username'

    # Tells Django that the UserManager class defined above should manage
    # objects of this type.
    objects = UserManager()

    def __str__(self):
        """
        Returns a string representation of this `User`.

        This string is used when a `User` is printed in the console.
        """
        return self.username

    @property
    def token(self):
        """
        Allows us to get a user's token by calling `user.token` instead of
        `user.generate_jwt_token().

        The `@property` decorator above makes this possible. `token` is called
        a "dynamic property".
        """
        return self._generate_jwt_token()

    def get_full_name(self):
        """
        This method is required by Django for things like handling emails.
        Typically this would be the user's first and last name. Since we do
        not store the user's real name, we return their username instead.
        """
        return self.username

    def get_short_name(self):
        """
        This method is required by Django for things like handling emails.
        Typically, this would be the user's first name. Since we do not store
        the user's real name, we return their username instead.
        """
        return self.username

    def _generate_jwt_token(self):
        """
        Generates a JSON Web Token and Refresh Token
        """

        refresh = RefreshToken.for_user(self)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

    def set_otp(self, length=4):
        raw_otp = random_number_generator(length, '0123456789')
        self.otp = make_password(raw_otp)
        self.otp_expiry = timezone.now() + datetime.timedelta(minutes=10)
        self.raw_otp = raw_otp

    def verify_otp(self, raw_otp):
        if self.otp is not None:
            try:
                salt = self.otp.split('$')[2]
                hashed_otp = make_password(raw_otp, salt)
                if self.otp == hashed_otp:
                    if timezone.now() <= self.otp_expiry:
                        return True
                    else:
                        return False
            except IndexError:
                return None
        else:
            return None


class Region(models.Model):
    """
    Region defines the area administered by a data entry admin
    """
    id = models.CharField(primary_key=True, default=hex_uuid, editable=False, unique=True, max_length=36)
    name = models.CharField(max_length=100)
    lat = models.FloatField(default=0.0)
    long = models.FloatField(default=0.0)

    def __str__(self):
        return "{}({}, {})".format(self.name, self.lat, self.long)


class DataEntryAdmin(models.Model):
    """
    For storing data entry admin profile

    Fields
    ------

    1. Name
    2. Department
    3. Designation
    4. Organisation
    5. Mobile number (Optional)


    Assigned region mapping can be handled using another table (tabled for now)
    Region radius is by default 1000 meters

    """
    id = models.CharField(primary_key=True, default=hex_uuid, editable=False, unique=True, max_length=36)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mobile_number = models.CharField(max_length=15, blank=True, null=True, default="")
    fullname = models.CharField(max_length=50)
    department = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    organisation = models.CharField(max_length=100)

    def __str__(self):
        return "{} : {} in {} at  {}".format(self.fullname, self.designation, self.department, self.organisation)


class DataEntryAdminRegion(models.Model):
    """
    For storing regions assigned to data entry admin
    """
    id = models.CharField(primary_key=True, default=hex_uuid, editable=False, unique=True, max_length=36)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    data_entry_admin = models.ForeignKey(DataEntryAdmin, on_delete=models.CASCADE)

    def __str__(self):
        return "{}({})".format(self.data_entry_admin.fullname, self.region.name)


class Citizen(models.Model):
    """
    For storing citizen profile information
    """
    id = models.CharField(primary_key=True, default=hex_uuid, editable=False, unique=True, max_length=36)
    iam_user_id = models.CharField(max_length=60, default="")
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mobile_number = models.CharField(max_length=15)
    fullname = models.CharField(max_length=50, blank=True, null=True, default="")
    dob = models.CharField(max_length=12, null=True, blank=True, default="01-01-1970")
    home_latitude = models.FloatField(default=0.0)
    home_longitude = models.FloatField(default=0.0)

    is_location_sync_enabled = models.BooleanField(default=False)

    def __str__(self):
        return self.mobile_number


class FCMPushNotificationRegistrationToken(Device):
    """
    FCMPushNotificationRegistrationToken

    Overriding the GCMDevice model provided by django push notifications package, to handle device_id commonly
    for both iOS and Android devices.
    """
    device_id = models.CharField(
        verbose_name="Device ID", blank=True, null=True, db_index=True,
        max_length=1024,
        help_text=
        "ANDROID_ID / TelephonyManager.getDeviceId() (always as hex) / UDID / UIDevice.identifierForVendor()"
    )

    registration_id = models.TextField(verbose_name="Registration ID", unique=SETTINGS["UNIQUE_REG_ID"])
    cloud_message_type = models.CharField(
        verbose_name="Cloud Message Type", max_length=3,
        choices=CLOUD_MESSAGE_TYPES, default="GCM",
        help_text="You should choose FCM or GCM"
    )
    objects = GCMDeviceManager()

    class Meta:
        verbose_name = "FCM Device"

    def send_message(self, message, **kwargs):
        from push_notifications.gcm import send_message as gcm_send_message

        data = kwargs.pop("extra", {})
        if message is not None:
            data["message"] = message

        return gcm_send_message(
            self.registration_id, data, self.cloud_message_type,
            application_id=self.application_id, **kwargs
        )
