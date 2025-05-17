from django.shortcuts import render
from base.base_views import (
    CustomViewSetV2,
)
from hospital.serializers import HospitalListSerializer, HospitalSerializer
from hospital.models import Hospital
from rest_framework.permissions import IsAuthenticated
from hospital.permissions import CanCreateDeleteHospital, CanUpdateHospital
from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter
from hospital.filters import HospitalFilterSet


# Create your views here.
class HospitalAPI(CustomViewSetV2):
    """
    This API is to create the Hospital
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = HospitalSerializer
    model_class = Hospital
    queryset = Hospital.objects.all()
    filter_backends = (filters.DjangoFilterBackend, SearchFilter)
    filterset_class = HospitalFilterSet

    search_fields = (
        "name",
        "description",
        "facilities",
    )

    def get_queryset(self):
        # only SuperAdmin can all user whereas other user can see on their hospital users only
        qs = super().get_queryset()
        user = self.request.user
        if user.is_anonymous:
            return qs.none()
        if user.is_superuser:
            return qs
        else:
            return qs.filter(id=self.request.user.hospital_id)

    def get_serializer_context(self):
        context = super(HospitalAPI, self).get_serializer_context()
        context.update({"request": self.request})
        return context

    def initial(self, request, *args, **kwargs):
        method = request.method
        if method == "GET":
            self.serializer_class = HospitalListSerializer
        elif method in ["POST", "DELETE"]:
            self.permission_classes = (CanCreateDeleteHospital,)
        elif method == "PUT":
            self.permission_classes = (CanUpdateHospital,)
        return super().initial(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.serializer_class = HospitalSerializer
        return super().retrieve(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
