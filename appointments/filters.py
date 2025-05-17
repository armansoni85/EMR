from base.filters import FilterBaseSet, filters
from .models import Appointment


class AppointmentFilterset(FilterBaseSet):
    class Meta:
        model = Appointment
        fields = [
            "doctor",
            "patient",
            "disease",
            "appointment_status",
            "appointment_datetime",
        ]
