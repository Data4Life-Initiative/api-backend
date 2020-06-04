from django.contrib import admin

from core.models import *

# Registering the database models in the django admin panel
# When registered these models can be manipulated from the admin panel

# proxy of models from authentication app
admin.site.register(ProxyFCMPushNotificationRegistrationToken)
admin.site.register(ProxyRegion)
admin.site.register(ProxyDataEntryAdminRegion)

# models from core app
admin.site.register(Disease)
admin.site.register(DiseaseInfectionStatus)
admin.site.register(PatientHistoricLocation)
admin.site.register(CitizenDiseaseRelation)
admin.site.register(AreaSeverityLevel)
admin.site.register(RiskAssessmentRecommendation)
admin.site.register(SelfScreeningQuestion)
admin.site.register(WellnessStatusOutcome)
admin.site.register(CitizenPushNotifications)
