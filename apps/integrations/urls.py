# integrations/urls.py - ÚNICO ARQUIVO DE URLs
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BrokermintDocumentViewSet

router = DefaultRouter()
router.register(r'documents', BrokermintDocumentViewSet)

app_name = 'integrations'

urlpatterns = [
    path('api/', include(router.urls)),
]
