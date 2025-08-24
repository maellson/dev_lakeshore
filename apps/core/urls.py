# apps/core/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import health_check, api_root_view, CountyViewSet, RealtorViewSet, HOAViewSet, api_schema_info

# Router para ViewSets do core
router = DefaultRouter()
router.register(r'counties', CountyViewSet, basename='county')
router.register(r'realtors', RealtorViewSet, basename='realtor')
router.register(r'hoas', HOAViewSet, basename='hoa')

app_name = 'core'
urlpatterns = [
    path('', api_root_view, name='api_root'),
    path('health/', health_check, name='health_check'),
    path('schema-info/', api_schema_info, name='api_schema_info'),


    # API endpoints

    # Counties API
    path('', include(router.urls)),
]
