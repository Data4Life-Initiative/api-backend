from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from rest_framework_nested import routers as drf_nested_routers
from rest_framework_simplejwt.views import TokenRefreshView

from authentication.views import DataEntryAdminLoginAPIView, CitizenSendOTPAPIView, \
    CitizenVerifyOTPAPIView, SuperAdminLoginAPIView, CitizenRegistrationAPIView, CitizenLoginUsingEmailAPIView
from citizen.views import CitizenLocationSyncAPIView, CitizenMapDataAPIView, CitizenProfileAPIView, CitizenQRCodeAPIView
from dashboard.views import StatsAPIView, MapDataAPIView, PatientHistoricLocationSyncConsentQRCodeView
from disease.views import DiseaseCRUDViewSet, DiseaseInfectionStatusCRUDViewSet
from patient.views import PatientHistoricLocationViewSet
from super_admin.views import AreaSeverityLevelCRUDViewSet, DataEntryAdminCRUDViewSet, \
    DataEntryAdminRegionViewSet, RegionCRUDViewSet, RiskAssessmentRecommendationCRUDViewSet, \
    SelfScreeningQuestionCRUDViewSet, WellnessStatusOutcomeCRUDViewSet

simple_router = drf_nested_routers.SimpleRouter()
simple_router.register(r'disease', DiseaseCRUDViewSet, basename='disease')
simple_router.register(r'region', RegionCRUDViewSet, basename='region')

disease_nested_router = drf_nested_routers.NestedSimpleRouter(
    simple_router, r'disease', lookup='disease')
disease_nested_router.register(
    r'infection-status', DiseaseInfectionStatusCRUDViewSet, basename='infection-status')

region_nested_router = drf_nested_routers.NestedSimpleRouter(
    simple_router, r'region', lookup='region')
region_nested_router.register(
    r'area-severity-level', AreaSeverityLevelCRUDViewSet, basename='area-severity-level')

router = routers.DefaultRouter()
router.register(r'region', RegionCRUDViewSet, basename='region_crud_view_set')
router.register(r'data-entry-admin', DataEntryAdminCRUDViewSet,
                basename='data_entry_admin_crud_view_set')
router.register(r'patient/historic-location',
                PatientHistoricLocationViewSet, basename='patient_historic_location')
router.register(r'risk-assessment-recommendation',
                RiskAssessmentRecommendationCRUDViewSet, basename='risk-assessment-recommendation')
router.register(r'self-screening-question',
                SelfScreeningQuestionCRUDViewSet, basename='self-screening-questions')
router.register(r'wellness-status',
                WellnessStatusOutcomeCRUDViewSet, basename='wellness-status')

urlpatterns = [
    path('v1/', include(router.urls)),
    path('admin/', admin.site.urls),
    url(r'^v1/', include('rest_framework.urls', namespace='rest_framework')),
    path('v1/', include(simple_router.urls)),
    path('v1/', include(disease_nested_router.urls)),
    path('v1/', include(region_nested_router.urls)),

    # authentication
    path('v1/auth/token/refresh/',
         TokenRefreshView.as_view(),
         name='token_refresh_api'),

    # dashboard
    path('v1/dashboard/stats/', StatsAPIView.as_view(),
         name='dashboard_stats_api'),
    path('v1/dashboard/map/data/', MapDataAPIView.as_view(),
         name='dashboard_map_data_api'),
    path('v1/dashboard/patient-historic-location/qr-code/', PatientHistoricLocationSyncConsentQRCodeView.as_view(),
         name='patient-historic-location-qr-code'),

    # super admin authentication
    path('v1/auth/login/super-admin/',
         SuperAdminLoginAPIView.as_view(),
         name='super_admin_login_api'),

    # data entry admin region assign, remove
    path('v1/data-entry-admin/<str:pk>/region/<str:region_id>/assign',
         DataEntryAdminRegionViewSet.as_view({'post': 'create'}), name='data_entry_admin_region_assign'),
    path('v1/data-entry-admin/<str:pk>/region/<str:region_id>/remove',
         DataEntryAdminRegionViewSet.as_view({'delete': 'destroy'}), name='data_entry_admin_region_remove'),

    # data entry admin authentication
    path('v1/auth/login/data-entry-admin/',
         DataEntryAdminLoginAPIView.as_view(),
         name='data_entry_admin_login_api'),

    # citizen registration
    path('v1/citizen/auth/register/', CitizenRegistrationAPIView.as_view(), name='citizen-register'),
    # citizen login using email, password
    path('v1/citizen/auth/login/', CitizenLoginUsingEmailAPIView.as_view(), name='citizen-login-using-email'),

    # citizen authentication
    path('v1/citizen/auth/send-otp/', CitizenSendOTPAPIView.as_view(),
         name='citizen_send_otp_api'),
    path('v1/citizen/auth/verify-otp/', CitizenVerifyOTPAPIView.as_view(),
         name='citizen_verify_otp_api'),

    # citizen profile
    path('v1/citizen/profile/', CitizenProfileAPIView.as_view(),
         name='citizen_profile_retrieve_update_api'),
    path('v1/citizen/qr/', CitizenQRCodeAPIView.as_view(), name='citizen_qr_api'),

    # citizen map data
    path('v1/citizen/map/data/', CitizenMapDataAPIView.as_view(),
         name='citizen_map_data_api'),

    # citizen location sync
    path('v1/citizen/location-sync/', CitizenLocationSyncAPIView.as_view(),
         name='citizen-location-sync')
]
