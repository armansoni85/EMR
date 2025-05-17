from rest_framework.permissions import BasePermission
from django.shortcuts import get_object_or_404
from user.choices import RoleType


class CanCreateAppointment(BasePermission):
    """Permission to check if a user can create an appointment."""

    def has_permission(self, request, view):
        user = request.user
        if user.is_authenticated:
            return user.role in [
                RoleType.patient.value[0],
                RoleType.hospital_admin.value[0],
            ]

        return False


class CanUpdateOrDeleteAppointment(BasePermission):
    """Permission to check if a user can update or delete an appointment."""

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False

        # Only doctors,hospital admin and patient can update or delete appointments
        return user.role in [
            RoleType.patient.value[0],
            RoleType.doctor.value[0],
            RoleType.hospital_admin.value[0],
        ]
