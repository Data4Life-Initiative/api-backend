from datetime import datetime

from rest_framework import serializers


class TimeStampField(serializers.Field):
    """
    Custom timestamp field
    """

    def to_representation(self, value):
        return value

    def to_internal_value(self, utc_timestamp_string):
        try:
            # converting UTC timestamp string to datetime object
            datetime_obj = datetime.fromtimestamp(int(utc_timestamp_string))
            return datetime_obj
        except:
            raise serializers.ValidationError("Please provide a valid UTC timestamp !")
