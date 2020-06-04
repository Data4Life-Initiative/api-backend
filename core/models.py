from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils import timezone

from authentication.models import Citizen, Region, FCMPushNotificationRegistrationToken, DataEntryAdminRegion
from authentication.utils import hex_uuid


class Disease(models.Model):
    """
    Disease

    For storing the available diseases in the system

    infection_status - [{"desc": "with symptoms"}, {"desc": "without symptoms"}]

    """
    id = models.CharField(primary_key=True, default=hex_uuid,
                          editable=False, unique=True, max_length=36)
    name = models.CharField(max_length=250, unique=True)

    def __str__(self):
        return self.name


class DiseaseInfectionStatus(models.Model):
    """
    DiseaseInfectionStatus

    For storing all the infection status associated with a disease
    """
    id = models.CharField(primary_key=True, default=hex_uuid,
                          editable=False, unique=True, max_length=36)
    disease = models.ForeignKey(Disease, on_delete=models.CASCADE)
    infection_status = models.CharField(max_length=250)

    def __str__(self):
        return "status:{} - disease:{}".format(self.infection_status, self.disease.name)


class PatientHistoricLocation(models.Model):
    """
    PatientHistoricLocation

    For storing historic locations of patients
    """
    id = models.CharField(primary_key=True, default=hex_uuid,
                          editable=False, unique=True, max_length=36)
    lat = models.FloatField(default=0.0)
    long = models.FloatField(default=0.0)
    recorded_date_time = models.DateTimeField()
    disease_infection_status = models.ForeignKey(
        DiseaseInfectionStatus, on_delete=models.CASCADE)

    @property
    def timestamp(self):
        return str(int(self.recorded_date_time.timestamp()))


class CitizenDiseaseRelation(models.Model):
    """
    CitizenDiseaseRelation

    For storing disease associated with a citizen and wellness
    """
    id = models.CharField(primary_key=True, default=hex_uuid,
                          editable=False, unique=True, max_length=36)
    citizen = models.ForeignKey(Citizen, on_delete=models.CASCADE)
    disease = models.ForeignKey(Disease, on_delete=models.CASCADE)
    wellness = models.CharField(max_length=50, default="")


class CitizenHistoricLocationDiseaseRelation(models.Model):
    """
    For storing historic locations of a citizen
    """
    id = models.CharField(primary_key=True, default=hex_uuid,
                          editable=False, unique=True, max_length=36)
    citizen = models.ForeignKey(Citizen, on_delete=models.CASCADE)
    disease = models.ForeignKey(Disease, on_delete=models.CASCADE)
    lat = models.FloatField()
    long = models.FloatField()
    location_name = models.CharField(max_length=250, blank=True, null=True, default="")
    recorded_date_time = models.DateTimeField()
    added_on = models.DateTimeField(default=timezone.now)

    @property
    def timestamp(self):
        return str(int(self.recorded_date_time.timestamp()))


class AreaSeverityLevel(models.Model):
    """
    AreaSeverityLevel

    For storing the severity levels used for area severity ranking.
    Severity level controls the intensity of patients within particular area in a region.
    Based on this, the different regions will color coded for better understanding

    Fields

    1. No of cases (within in `x` metre radius)
    2. Description - Label for the severity level for e.g. OK, Caution, Warning e.t.c
    3. Color code - Hexadecimal color, used for color coding maps for better visual understanding
    4. Region (foreign key) - Which region the severity level is applicable
    """

    id = models.CharField(primary_key=True, default=hex_uuid,
                          editable=False, unique=True, max_length=36)
    color_code = models.CharField(max_length=12)
    no_of_cases = models.IntegerField(default=1)
    description = models.TextField()
    region = models.ForeignKey(Region, on_delete=models.CASCADE)


class RiskAssessmentRecommendation(models.Model):
    """
    RiskAssessmentRecommendation

    For risk assessment recommendations which are the different outcomes when you perform risk analysis

    Fields

    1. Recommendation - A short text describing the outcome
    2. Recommendation detail - Further elaboration the recommendation with what measures needs to taken based on the outcome

    Each outcome has point range, based on which the outcome is chosen

    3. Point upper limit
    4. Point lower limit

    """
    id = models.CharField(primary_key=True, default=hex_uuid,
                          editable=False, unique=True, max_length=36)
    recommendation = models.CharField(max_length=250)
    recommendation_detail = models.TextField()
    point_upper_limit = models.FloatField()
    point_lower_limit = models.FloatField()


class SelfScreeningQuestion(models.Model):
    """
    SelfScreeningQuestion

    For storing the self screening questions to obtain the wellness status of an individual

    Fields

    1. Question
    2. Instruction
    3. Choices (List of dicts)

    [
        {
            "text"
            "points"
        }
    ]

    """
    id = models.CharField(primary_key=True, default=hex_uuid,
                          editable=False, unique=True, max_length=36)
    instruction = models.TextField()
    question = models.TextField()
    choices = JSONField(default=list)


class WellnessStatusOutcome(models.Model):
    """
    WellnessStatusOutcome

    For storing all the possible wellness status outcomes

    Fields

    1. Outcome

    Each outcome has point range, based on which the outcome is chosen

    2. Point upper limit
    3. Point lower limit
    """
    id = models.CharField(primary_key=True, default=hex_uuid,
                          editable=False, unique=True, max_length=36)
    outcome = models.CharField(max_length=80)
    point_upper_limit = models.FloatField()
    point_lower_limit = models.FloatField()


CITIZEN_PUSH_NOTIFICATION_TYPES = (
    ('CONTACT-TRACING', 'Contact tracing'),
    ('HOTSPOT-PROXIMITY', 'Hotspot proximity'),
    ('ANNOUNCEMENT', 'General announcement')
)


class CitizenPushNotifications(models.Model):
    """
    CitizenPushNotifications

    For storing all the push notifications send to the citizens

    Types of notifications

    1. Contact tracing - Triggered when performing contact tracing
    2. Hotspot proximity - Triggered when in proximity of `x` metres of hotspot
    3. General announcement
    """
    id = models.CharField(primary_key=True, default=hex_uuid,
                          editable=False, unique=True, max_length=36)
    type = models.CharField(max_length=50, choices=CITIZEN_PUSH_NOTIFICATION_TYPES)
    title = models.CharField(max_length=100)
    body = models.CharField(max_length=500)
    is_read = models.BooleanField(default=False)
    citizen = models.ForeignKey(Citizen, on_delete=models.CASCADE)
    added_on = models.DateTimeField(default=timezone.now)


class MobileNumberWhitelist(models.Model):
    """
    MobileNumberWhitelist

    For storing all the all citizen mobile numbers that are allowed to login to citizen app using one time password
    """
    id = models.CharField(primary_key=True, default=hex_uuid,
                          editable=False, unique=True, max_length=36)
    mobile_number = models.CharField(unique=True, max_length=18)


# A hack to show models from authentication app under core app in django admin panel
# Reference - https://stackoverflow.com/questions/10561091/group-models-from-different-app-object-into-one-admin-block
# proxy models
class ProxyFCMPushNotificationRegistrationToken(FCMPushNotificationRegistrationToken):
    class Meta:
        proxy = True
        verbose_name = FCMPushNotificationRegistrationToken._meta.verbose_name
        verbose_name_plural = FCMPushNotificationRegistrationToken._meta.verbose_name_plural


class ProxyRegion(Region):
    class Meta:
        proxy = True
        verbose_name = Region._meta.verbose_name
        verbose_name_plural = Region._meta.verbose_name_plural


class ProxyDataEntryAdminRegion(DataEntryAdminRegion):
    class Meta:
        proxy = True
        verbose_name = DataEntryAdminRegion._meta.verbose_name
        verbose_name_plural = DataEntryAdminRegion._meta.verbose_name_plural
