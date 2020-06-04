from rest_framework import serializers

from core.custom_fields import TimeStampField
from core.models import PatientHistoricLocation, DiseaseInfectionStatus


class HistoricLocationDataSerializer(serializers.Serializer):
    """
    Historic location serializer
    """
    lat = serializers.FloatField(required=True)
    long = serializers.FloatField(required=True)
    timestamp = serializers.CharField(required=True)


class PatientHistoricLocationBulkSerializer(serializers.Serializer):
    """
    PatientHistoricLocationBulkSerializer

    Serializes the bulk patient historic location creation data.
    """
    historic_locations = HistoricLocationDataSerializer(many=True)
    infection_status_id = serializers.CharField()

    def validate_infection_status_id(self, infection_status_id):
        try:
            DiseaseInfectionStatus.objects.get(id=infection_status_id)
        except DiseaseInfectionStatus.DoesNotExist:
            raise serializers.ValidationError('Please provide a valid infection status ID !')

        return infection_status_id


class PatientHistoricLocationSerializer(serializers.ModelSerializer):
    """
    PatientHistoricLocationSerializer

    Serializes the patient historic location data model
    """
    lat = serializers.FloatField(required=True)
    long = serializers.FloatField(required=True)
    timestamp = TimeStampField(required=True)
    id = serializers.CharField(read_only=True)

    class Meta:
        model = PatientHistoricLocation
        fields = ('lat', 'long', 'timestamp', 'id')

    def create(self, validated_data):
        infection_status = validated_data.get('infection_status', None)
        recorded_date_time = validated_data.get('timestamp')

        if not infection_status:
            raise serializers.ValidationError('Please provide a valid infection status object!')

        if not isinstance(infection_status, DiseaseInfectionStatus):
            raise serializers.ValidationError('Please provide a valid infection status object!')

        return PatientHistoricLocation.objects.create(lat=validated_data.get('lat'),
                                                      long=validated_data.get('long'),
                                                      recorded_date_time=recorded_date_time,
                                                      disease_infection_status=infection_status)

    def update(self, instance, validated_data):
        instance.latitude = validated_data.get('latitude', instance.latitude)
        instance.longitude = validated_data.get('longitude', instance.longitude)
        instance.recorded_date_time = validated_data.get('timestamp', instance.recorded_date_time)
        instance.save()
        return instance
