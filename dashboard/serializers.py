from rest_framework import serializers

from patient.serializers import HistoricLocationDataSerializer


class StatSerializer(serializers.Serializer):
    immunized = serializers.FloatField()
    naturally_immune = serializers.FloatField()
    currently_infected = serializers.FloatField()


class MapDataSerializer(serializers.Serializer):
    historic_locations = HistoricLocationDataSerializer(many=True)
