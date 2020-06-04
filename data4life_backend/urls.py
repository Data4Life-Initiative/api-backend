from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from push_notifications.models import APNSDevice, GCMDevice, WNSDevice, WebPushDevice
from rest_framework import routers
from rest_framework_nested import routers as drf_nested_routers

from authentication.views import *
from citizen.views import *
from dashboard.views import StatsAPIView, MapDataAPIView, PatientHistoricLocationSyncConsentQRCodeView
from disease.views import DiseaseCRUDViewSet, DiseaseInfectionStatusCRUDViewSet
from patient.views import PatientHistoricLocationViewSet
from super_admin.views import *

simple_router = drf_nested_routers.SimpleRouter()

# disease CRUD
simple_router.register(r'disease', DiseaseCRUDViewSet, basename='disease')
simple_router.register(r'region', RegionCRUDViewSet, basename='region')

disease_nested_router = drf_nested_routers.NestedSimpleRouter(
    simple_router, r'disease', lookup='disease')

# CRUD operation for infection status
disease_nested_router.register(
    r'infection-status', DiseaseInfectionStatusCRUDViewSet, basename='infection-status')

region_nested_router = drf_nested_routers.NestedSimpleRouter(
    simple_router, r'region', lookup='region')

# CRUD operations for severity levels defined for an area
region_nested_router.register(
    r'area-severity-level', AreaSeverityLevelCRUDViewSet, basename='area-severity-level')

router = routers.DefaultRouter()

# regions CRUD
router.register(r'region', RegionCRUDViewSet, basename='region_crud_view_set')

# data entry admin CRUD
router.register(r'data-entry-admin', DataEntryAdminCRUDViewSet,
                basename='data_entry_admin_crud_view_set')

# patient historic location CRUD
router.register(r'patient/historic-location',
                PatientHistoricLocationViewSet, basename='patient_historic_location')

# risk assessment recommendations CRUD
router.register(r'risk-assessment-recommendation',
                RiskAssessmentRecommendationCRUDViewSet, basename='risk-assessment-recommendation')

# self screening questions CRUD
router.register(r'self-screening-question',
                SelfScreeningQuestionCRUDViewSet, basename='self-screening-questions')

# wellness status CRUD
router.register(r'wellness-status',
                WellnessStatusOutcomeCRUDViewSet, basename='wellness-status')

# citizen mobile number whitelisting CRUD
router.register(r'super-admin/citizen-whitelist', MobileNumberWhitelistCRUDViewSet, basename='citizen-whitelist')

# citizen historic locations CRUD
router.register(r'citizen/historic-location', CitizenHistoricLocationDiseaseRelationViewSet,
                basename='citizen-historic-location')

urlpatterns = [
    path('v1/', include(router.urls)),
    path('admin/', admin.site.urls),
    url(r'^v1/', include('rest_framework.urls', namespace='rest_framework')),
    path('v1/', include(simple_router.urls)),
    path('v1/', include(disease_nested_router.urls)),
    path('v1/', include(region_nested_router.urls)),

    # refresh access tokens
    path('v1/auth/token/refresh/',
         RefreshTokenAPIView.as_view(),
         name='refresh-token'),

    # dashboard
    path('v1/dashboard/stats/', StatsAPIView.as_view(),
         name='dashboard_stats_api'),
    path('v1/dashboard/map/data/', MapDataAPIView.as_view(),
         name='dashboard_map_data_api'),
    path('v1/dashboard/patient-consent-qr-code/', PatientHistoricLocationSyncConsentQRCodeView.as_view(),
         name='patient-historic-location-qr-code'),

    # super admin authentication
    path('v1/auth/login/super-admin/',
         SuperAdminLoginAPIView.as_view(),
         name='super_admin_login_api'),

    # citizens listing
    path('v1/citizen/', CitizenListingAPIView.as_view(), name="citizen-listing"),

    # send push notifications
    path('v1/super-admin/send-push-notification/', SendPushNotificationToCitizenAPIView.as_view(),
         name='send-push-notification'),
    path('v1/super-admin/send-push-notifications/', SendPushNotificationToAllCitizenAPIView.as_view(),
         name='send-push-notifications'),

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

    # citizen device push notification token registration
    path('v1/citizen/device/register/', PushNotificationDeviceRegistrationTokenAPIView.as_view(),
         name='citizen-device-register'),
    path('v1/citizen/device/deregister/', PushNotificationDeviceRegistrationTokenDeleteAPIView.as_view(),
         name='citizen-device-deregister'),

    # citizen notifications
    path('v1/citizen/notification/', NotificationsListingAPIView.as_view(), name='citizen-notifications-listing'),
    path('v1/citizen/notification/<str:pk>/<str:notification_read_status>/', NotificationReadStatusUpdate.as_view(),
         name='citizen-notification-mark-as-read'),
    path('v1/citizen/notification/<str:pk>/<str:notification_read_status>/', NotificationReadStatusUpdate.as_view(),
         name='citizen-notifications-mark-as-unread'),

    # citizen - mock risk assessment score
    path('v1/citizen/perform-risk-assessment/', PerformRiskAssessmentAPI.as_view(), name='perform-risk-assessment')
]

# Hiding third party models associated with push notifications in django admin panel
admin.autodiscover()
admin.site.unregister(APNSDevice)
admin.site.unregister(GCMDevice)
admin.site.unregister(WNSDevice)
admin.site.unregister(WebPushDevice)
