import os

from django.db.models import Q

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'data4life_backend.settings')

import django

django.setup()

from django.conf import settings

from core.models import Disease, DiseaseInfectionStatus, RiskAssessmentRecommendation, WellnessStatusOutcome
from authentication.models import User

DISEASES = [
    {"name": "COVID-19", "infection_status": [{"desc": "with symptoms"}, {"desc": "without symptoms"}]},
    {"name": "SARS", "infection_status": [{"desc": "with symptoms"}, {"desc": "without symptoms"}]},
    {"name": "Ebola", "infection_status": [{"desc": "with symptoms"}, {"desc": "without symptoms"}]},
    {"name": "Smallpox", "infection_status": [{"desc": "with symptoms"}, {"desc": "without symptoms"}]},
    {"name": "Influenza", "infection_status": [{"desc": "with symptoms"}, {"desc": "without symptoms"}]},
    {"name": "Yellow fever", "infection_status": [{"desc": "with symptoms"}, {"desc": "without symptoms"}]},
    {"name": "Spanish flu", "infection_status": [{"desc": "with symptoms"}, {"desc": "without symptoms"}]}
]

print("\n1. Adding init disease and infection status records to the system\n")

for disease in DISEASES:
    if Disease.objects.filter(name__iexact=disease["name"]).count() == 0:
        print("\t> Created {} disease record".format(disease["name"]))
        disease_obj = Disease.objects.create(name=disease["name"])
        for infection_status in disease["infection_status"]:
            DiseaseInfectionStatus.objects.create(disease=disease_obj, infection_status=infection_status)

print("\n2. Creating admin user\n")

super_admins = settings.SUPER_ADMINS
if not isinstance(super_admins, list):
    raise TypeError("SUPER_ADMINS configuration must be a list of super admin user dicts!")

for super_admin in super_admins:
    if not isinstance(super_admin, dict):
        raise TypeError("SUPER_ADMINS configuration must be a list of super admin user dicts!")

    if not ('USERNAME' in super_admin and 'EMAIL' in super_admin and 'PASSWORD' in super_admin):
        raise TypeError("SUPER_ADMINS configuration must be a list of super admin user dicts!")

    if User.objects.filter(Q(username=super_admin['USERNAME']) | Q(email=super_admin['EMAIL']) | Q(
            username=super_admin['EMAIL'])).count() == 0:
        print("\t> Create super admin record for {}".format(super_admin['EMAIL']))
        User.objects.create_superuser(username=super_admin['EMAIL'],
                                      email=super_admin['EMAIL'],
                                      password=super_admin['PASSWORD'])

# Populate risk assessment recommendation model
possible_recommendations = [

    {
        "recommendation": "Stay cautious as this is a serious pandemic",
        "upper_limit": 2,
        "lower_limit": 1,
        "recommendation_detail": "Based on your health profile and based on your contact tracing record, you are perceived to have low risk of being infected. We recommend you to stay cautious as this is a serious pandemic."
    },
    {
        "recommendation": "Stay at home with limited movements",
        "upper_limit": 4.9,
        "lower_limit": 2.1,
        "recommendation_detail": "Based on your health profile and based on your contact tracing record, you are perceived to have low risk of being infected. We recommend you to stay at home with limited movements."
    },
    {
        "recommendation": "Self Quarantine",
        "upper_limit": 6.9,
        "lower_limit": 5,
        "recommendation_detail": "Based on your health profile and based on your contact tracing record, you are perceived to be at risk of infected. We recommend you to stay indoor and self quarantine."
    },
    {
        "recommendation": "Get yourself tested",
        "upper_limit": 8.9,
        "lower_limit": 7,
        "recommendation_detail": "Based on your health profile and based on your contact tracing record, you are perceived to be at higher risk of infected. We recommend you to get tested."
    },
    {
        "recommendation": "Stay in isolation as you are positive",
        "upper_limit": 10,
        "lower_limit": 9,
        "recommendation_detail": "Based on your health profile and based on your contact tracing record, you are perceived to be infected. We recommend you to stay isolated."
    }
]

print("\n1. Adding possible risk assessment recommendations to the system\n")

for risk_assessment_recommendation in possible_recommendations:
    RiskAssessmentRecommendation.objects.create(recommendation=risk_assessment_recommendation['recommendation'],
                                                recommendation_detail=risk_assessment_recommendation[
                                                    'recommendation_detail'],
                                                point_upper_limit=risk_assessment_recommendation['upper_limit'],
                                                point_lower_limit=risk_assessment_recommendation['lower_limit'])

possible_wellness_status_outcomes = [
    {"outcome": "Healthy", "upper_limit": 50, "lower_limit": 0.1},
    {"outcome": "Healthy, but susceptible", "upper_limit": 100, "lower_limit": 50}
]

print("\n1. Adding possible wellness status outcomes to the system\n")

for wellness_status_outcome in possible_wellness_status_outcomes:
    WellnessStatusOutcome.objects.create(outcome=wellness_status_outcome['outcome'],
                                         point_upper_limit=wellness_status_outcome['upper_limit'],
                                         point_lower_limit=wellness_status_outcome['lower_limit'])
