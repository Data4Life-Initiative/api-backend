import datetime

from rest_framework import serializers
from django.db import models

from core.models import CitizenDiseaseRelation, CitizenLocationSync, WellnessStatusOutcome
from patient.serializers import HistoricLocationDataSerializer


class CitizenHistoricLocationDataSerializer(HistoricLocationDataSerializer):
    location_name = serializers.CharField(max_length=250)


class CitizenSerializer(serializers.ModelSerializer):
    """
    CitizenSerializer

    Serializes the citizen data
    """
    id = serializers.CharField(source='citizen.id', read_only=True)
    email = serializers.CharField(read_only=True, source='citizen.user.email')
    mobile_number = serializers.CharField(
        source='citizen.mobile_number', read_only=True)
    fullname = serializers.CharField(
        max_length=50, required=False, source='citizen.fullname')

    # date of birth
    dob = serializers.CharField(source='citizen.dob', required=False)

    # citizen home location
    home_latitude = serializers.FloatField(
        required=False, source='citizen.home_latitude')
    home_longitude = serializers.FloatField(
        required=False, source='citizen.home_longitude')

    # for serializing the citizen historic location data
    historic_locations = CitizenHistoricLocationDataSerializer(
        many=True, required=False)

    wellness = serializers.CharField(required=False)

    class Meta:
        model = CitizenDiseaseRelation
        fields = (
            'id', 'email', 'fullname', 'dob', 'home_latitude', 'home_longitude', 'historic_locations', 'wellness',
            'mobile_number')

    def validate_dob(self, dob):
        try:
            datetime.datetime.strptime(dob, '%d-%m-%Y')
        except ValueError:
            raise serializers.ValidationError(
                "Incorrect date format, should be dd-mm-yyyy")
        return dob

    def validate_wellness(self, wellness):
        if len(wellness) > 0:
            if WellnessStatusOutcome.objects.filter(outcome__iexact=wellness).count() == 0:
                raise serializers.ValidationError(
                    'Please provide a valid wellness status !')
        return wellness

    def update(self, instance, validated_data):

        citizen_data = validated_data.get('citizen')

        if citizen_data:
            instance.citizen.fullname = citizen_data.get(
                'fullname', instance.citizen.fullname)
            instance.citizen.dob = citizen_data.get(
                'dob', instance.citizen.dob)
            instance.citizen.home_latitude = citizen_data.get(
                'home_latitude', instance.citizen.home_latitude)
            instance.citizen.home_longitude = citizen_data.get(
                'home_longitude', instance.citizen.home_longitude)
            instance.citizen.save()

        instance.historic_locations = validated_data.get(
            'historic_locations', instance.historic_locations)
        instance.wellness = validated_data.get('wellness', instance.wellness)
        instance.save()

        return instance


class QRSerializer(serializers.Serializer):
    """
    This serializer is the output of create qr code
    """
    file_type = serializers.CharField(max_length=5)
    image_base64 = serializers.CharField(max_length=300)


class CitizenLocationSyncSerializer(serializers.ModelSerializer):
    """
    CitizenLocationSyncSerializer

    Serializes citizen continous location updates
    
    On each location update, the location coords are checked to see if 
    they are in `x` meters proximity of a historic location of patients (locations which are expired yet)
    
    If in proximity trigger notification to all citizen devices, if difference in time between last
    notification is `y` seconds
    """
    id = serializers.CharField(read_only=True)
    lat = serializers.FloatField()
    long = serializers.FloatField()
    timestamp = serializers.SerializerMethodField()

    def get_added_on(self, instance):
        return instance.added_on.timestamp

    class Meta:
        model = CitizenLocationSync
        fields = ('id', 'lat', 'long', 'timestamp')

    def create(self, validated_data):
        citizen = validated_data.pop('citizen')
        lat = validated_data.get('lat')
        long = validated_data.get('long')

        # Do this in background thread for non blocking execution
        # Todo: Check if the location is within `x` meters of any of historic locations of patients
        # Todo: If in proximity, then trigger notification if difference between last notification is `y` seconds

        return CitizenLocationSync.objects.create(lat=lat,
                                                  long=long,
                                                  citizen=citizen)
