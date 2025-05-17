# importing from the DRF libraries
from rest_framework.permissions import BasePermission

# importing from the app
from user.choices import RoleType


class CanCreateUpdateConsultation(BasePermission):
    """Checking if user can create,update consultation"""

    def has_permission(self, request, view):
        user = request.user
        if user.is_authenticated:
            if user.is_superuser:
                return True
            if user.role == RoleType.doctor.value[0]:
                return True
        return False
