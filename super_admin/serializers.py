from rest_framework import serializers

from authentication.models import Region, DataEntryAdmin, User, DataEntryAdminRegion
from core.models import AreaSeverityLevel, RiskAssessmentRecommendation, SelfScreeningQuestion, WellnessStatusOutcome
from core.utils import validate_hexadecimal_color_code


class AreaSeverityLevelListSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)

    class Meta:
        model = AreaSeverityLevel
        fields = ('id', 'color_code', 'no_of_cases', 'description')


class RegionSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    name = serializers.CharField(required=True, max_length=100, min_length=2)
    lat = serializers.FloatField(required=True)
    long = serializers.FloatField(required=True)
    area_severity_levels = AreaSeverityLevelListSerializer(
        many=True, source='areaseveritylevel_set', read_only=True)

    class Meta:
        model = Region
        fields = ('id', 'name', 'lat', 'long', 'area_severity_levels')


class DataEntryAdminSerializerBase(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    email = serializers.EmailField(max_length=255)
    fullname = serializers.CharField(max_length=50)
    designation = serializers.CharField(max_length=100)
    department = serializers.CharField(max_length=100)
    organisation = serializers.CharField(max_length=100)
    mobile_number = serializers.CharField(max_length=15,
                                          required=False,
                                          default="")

    regions = serializers.SerializerMethodField(read_only=True)

    def validate_email(self, email):
        if User.objects.filter(username=email).count() != 0:
            raise serializers.ValidationError(
                'User with respective email already exists!'
            )

        return email

    def get_regions(self, instance):

        # Todo : Why this check is performed ?
        if not hasattr(instance, 'id'):
            return []

        data_entry_admin_regions = DataEntryAdminRegion.objects.filter(
            data_entry_admin__id=instance.id)
        return [RegionSerializer(data_entry_admin_region.region).data for data_entry_admin_region in
                data_entry_admin_regions]


class DataEntryAdminSerializerWithPassword(DataEntryAdminSerializerBase):
    password = serializers.CharField(max_length=128,
                                     min_length=5,
                                     allow_blank=False,
                                     trim_whitespace=True,
                                     write_only=True)

    def create(self, validated_data):
        email = validated_data.get('email')
        password = validated_data.get('password')
        mobile_number = validated_data.get('mobile_number')
        fullname = validated_data.get('fullname')
        department = validated_data.get('department')
        designation = validated_data.get('designation')
        organisation = validated_data.get('organisation')

        user = User.objects.create_user(username=email,
                                        email=email,
                                        password=password)
        data_entry_admin = DataEntryAdmin.objects.create(user=user,
                                                         mobile_number=mobile_number,
                                                         fullname=fullname,
                                                         department=department,
                                                         designation=designation,
                                                         organisation=organisation)

        return {
            "id": data_entry_admin.id,
            "email": email,
            "mobile_number": mobile_number,
            "fullname": fullname,
            "department": department,
            "designation": designation,
            "organisation": organisation,
            "regions": self.get_regions(data_entry_admin)
        }


class DataEntryAdminSerializerWithoutPassword(DataEntryAdminSerializerBase):
    email = serializers.EmailField(source='user.email', read_only=True)

    def update(self, instance, validated_data):
        instance.mobile_number = validated_data.get(
            'mobile_number', instance.mobile_number)
        instance.fullname = validated_data.get('fullname', instance.fullname)
        instance.department = validated_data.get(
            'department', instance.department)
        instance.designation = validated_data.get(
            'designation', instance.designation)
        instance.organisation = validated_data.get(
            'organisation', instance.organisation)
        instance.save()

        return {
            "id": instance.id,
            "email": instance.user.email,
            "mobile_number": instance.mobile_number,
            "fullname": instance.fullname,
            "department": instance.department,
            "designation": instance.designation,
            "organisation": instance.organisation,
            "regions": self.get_regions(instance)
        }


class AreaSeverityLevelSerializer(serializers.Serializer):
    """
    AreaSeverityLevelSerializer

    Serializes create, update area severity level data
    """
    id = serializers.CharField(read_only=True)
    color_code = serializers.CharField(max_length=12)
    no_of_cases = serializers.IntegerField()
    description = serializers.CharField()

    def validate_no_of_cases(self, no_of_cases):
        """
        Validates no of cases must be more than 0

        :param no_of_cases:
        :return:
        """
        if no_of_cases < 1:
            raise serializers.ValidationError(
                'No of cases must be greater than 0 !')
        return no_of_cases

    def validate_color_code(self, color_code):
        """
        Validate the color code to be a valid hexadecimal color code

        :param color_code:
        :return:
        """
        if not validate_hexadecimal_color_code(color_code):
            raise serializers.ValidationError(
                'Please provide a valid hexadecimal color code !')
        return color_code

    def create(self, validated_data):
        """
        Creates the severity level for an area in a region

        :param validated_data:
        :return:
        """
        region = validated_data.pop('region')
        return AreaSeverityLevel.objects.create(**validated_data, region=region)

    def update(self, instance, validated_data):
        """
        Updates the severity level for an area in a region

        :param instance:
        :param validated_data:
        :return:
        """
        instance.color_code = validated_data.get(
            'color_code', instance.color_code)
        instance.no_of_cases = validated_data.get(
            'no_of_cases', instance.no_of_cases)
        instance.description = validated_data.get(
            'description', instance.description)
        instance.save()

        return instance


class RiskAssessmentRecommendationSerializer(serializers.ModelSerializer):
    """
    RiskAssessmentRecommendationSerializer

    Serializes CRUD data for risk assessment recommendations
    """
    id = serializers.CharField(read_only=True)

    def validate(self, data):
        point_upper_limit = data.get('point_upper_limit')
        point_lower_limit = data.get('point_lower_limit')

        if point_lower_limit and point_upper_limit:
            if point_lower_limit <= 0.0 or point_upper_limit <= 0.0:
                raise serializers.ValidationError(
                    'Points must be greater than 0.0 !')

            if point_upper_limit <= point_lower_limit:
                raise serializers.ValidationError(
                    'Upper limit must be greater than lower limit !')

            if point_lower_limit >= point_upper_limit:
                raise serializers.ValidationError(
                    'Lower limit must be less than upper limit !')

        return data

    class Meta:
        model = RiskAssessmentRecommendation
        fields = ('id', 'recommendation', 'recommendation_detail',
                  'point_upper_limit', 'point_lower_limit')


class SelfScreeningQuestionChoiceSerializer(serializers.Serializer):
    """
    SelfScreeningQuestionChoiceSerializer

    Serializes choices for a self screening question
    """
    text = serializers.CharField(max_length=250, min_length=3)
    points = serializers.FloatField()

    def validate_points(self, points):
        if points <= 0.0:
            raise serializers.ValidationError(
                'Points must be greater than 0.0 !')
        return points


class SelfScreeningQuestionSerializer(serializers.ModelSerializer):
    """
    SelfScreeningQuestionSerializer

    Serializes CRUD data for self screening questions
    """
    id = serializers.CharField(read_only=True)
    choices = SelfScreeningQuestionChoiceSerializer(many=True, required=True)

    def validate_question(self, question):
        if len(question) < 3:
            raise serializers.ValidationError(
                'Question must be atleast 3 characters long !')
        return question

    class Meta:
        model = SelfScreeningQuestion
        fields = ('id', 'question', 'instruction', 'choices')


class WellnessStatusOutcomeSerializer(serializers.ModelSerializer):
    """
    WellnessStatusOutcomeSerializer

    Serializes CRUD data for wellness status outcomes
    """
    id = serializers.CharField(read_only=True)

    def validate(self, data):
        point_upper_limit = data.get('point_upper_limit')
        point_lower_limit = data.get('point_lower_limit')

        if point_lower_limit and point_upper_limit:
            if point_lower_limit <= 0.0 or point_upper_limit <= 0.0:
                raise serializers.ValidationError(
                    'Points must be greater than 0.0 !')

            if point_upper_limit <= point_lower_limit:
                raise serializers.ValidationError(
                    'Upper limit must be greater than lower limit !')

            if point_lower_limit >= point_upper_limit:
                raise serializers.ValidationError(
                    'Lower limit must be less than upper limit !')

        return data

    class Meta:
        model = WellnessStatusOutcome
        fields = ('id', 'outcome', 'point_upper_limit', 'point_lower_limit')
