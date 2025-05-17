from rest_framework.permissions import BasePermission


class CanCreateDeleteHospital(BasePermission):
    """Checking if user can create ,delete hospital"""

    def has_permission(self, request, view):
        user = request.user
        if user.is_authenticated and user.is_superuser:
            return True
        return False


class CanUpdateHospital(BasePermission):
    """Checking if user can update hospital or not."""

    def has_permission(self, request, view):
        user = request.user
        if user.is_authenticated and user.is_superuser:
            return True
        # check if user's role is hospital_admin then can updates its own data only
        if view.kwargs["pk"] == str(user.hospital_id):
            return True
        return False
