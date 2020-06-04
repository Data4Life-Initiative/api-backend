from rest_framework import serializers

from patient.serializers import HistoricLocationDataSerializer


class StatSerializer(serializers.Serializer):
    """
    Serializes disease related stats for displaying in data entry admin dashboard
    """
    immunized = serializers.FloatField()
    naturally_immune = serializers.FloatField()
    currently_infected = serializers.FloatField()


class MapDataSerializer(serializers.Serializer):
    """
    Serializes patient historic data for plotting in data entry dashboard maps
    """
    historic_locations = HistoricLocationDataSerializer(many=True)
