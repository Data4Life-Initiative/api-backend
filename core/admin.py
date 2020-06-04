from django.contrib import admin

from core.models import Disease, PatientHistoricLocation, DiseaseInfectionStatus, CitizenLocationSync, \
    CitizenDiseaseRelation, AreaSeverityLevel, RiskAssessmentRecommendation, SelfScreeningQuestion, \
    WellnessStatusOutcome

admin.site.register(Disease)
admin.site.register(DiseaseInfectionStatus)
admin.site.register(PatientHistoricLocation)
admin.site.register(CitizenLocationSync)
admin.site.register(CitizenDiseaseRelation)
admin.site.register(AreaSeverityLevel)
admin.site.register(RiskAssessmentRecommendation)
admin.site.register(SelfScreeningQuestion)
admin.site.register(WellnessStatusOutcome)
