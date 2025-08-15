from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ICDCodeViewSet, CPTCodeViewSet

router = DefaultRouter()
router.register(r"icd-codes", ICDCodeViewSet, basename="icdcode")
router.register(r"cpt-codes", CPTCodeViewSet, basename="cptcode")

urlpatterns = [
    path("", include(router.urls)),
]

