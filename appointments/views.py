from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from base.base_views import (
    CustomViewSetV2,
)
from .models import Appointment
from .serializers import AppointmentSerializer, AppointmentListSerializer
from .filters import AppointmentFilterset
from user.choices import RoleType
from .permissions import CanCreateAppointment, CanUpdateOrDeleteAppointment


class AppointmentAPI(CustomViewSetV2):
    """
    Handles listing all appointments and creating a new appointment.
    Allows filtering and searching by patient name, date of birth, and disease.
    Restricts results to appointments for the user's hospital.
    """

    serializer_class = AppointmentSerializer
    permission_classes = [
        IsAuthenticated
    ]  # Ensure only authenticated users can access the API
    model_class = Appointment
    queryset = Appointment.objects.all()
    # Add filtering and searching
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = AppointmentFilterset
    search_fields = [
        "patient__first_name",
        "patient__last_name",
        "patient__dob",
        "disease",
        "reason_of_visit",
    ]

    def get_queryset(self):
        qs = self.queryset.select_related("patient", "doctor")
        user = self.request.user
        if user.is_superuser:
            return qs
        if user.role == RoleType.hospital_admin.value[0]:
            # if user role is hospital_admin ,he can see all appointment of his/her hospital
            return qs.filter(
                Q(doctor__hospital_id=user.hospital_id)
                | Q(patient__hospital_id=user.hospital_id)
            )

        return qs.filter(Q(doctor_id=user.id) | Q(patient_id=user.id))

    def initial(self, request, *args, **kwargs):
        method = request.method
        if method == "POST":
            self.permission_classes = (CanCreateAppointment,)
        elif method in ["PUT", "DELETE"]:
            self.permission_classes = (CanUpdateOrDeleteAppointment,)
        return super().initial(request, *args, **kwargs)

    def get_serializer_context(self):
        context = super(AppointmentAPI, self).get_serializer_context()
        context.update({"request": self.request})
        return context

    def get(self, request, *args, **kwargs):
        self.serializer_class = AppointmentListSerializer
        return super().retrieve(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
