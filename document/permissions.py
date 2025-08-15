from rest_framework.permissions import BasePermission
from user.choices import RoleType
from document.models import MedicalDocument


class CanUploadMedicalDocument(BasePermission):
    """Checking if user can upload document"""

    def has_permission(self, request, view):
        user = request.user
        if user.is_authenticated and any(
            [
                user.is_superuser,
                user.role
                in [
                    RoleType.patient.value[0],
                    RoleType.doctor.value[0],
                    RoleType.hospital_admin.value[0],
                ],
            ]
        ):
            return True
        return False


class CanUpdateDeleteMedicalDocument(BasePermission):
    """Checking if user can update,delete medical document or not. Note: user can modify their document only except admin"""

    def has_permission(self, request, view):
        user = request.user
        if user.is_authenticated and any(
            [
                user.is_superuser,
                user.role
                in [
                    RoleType.patient.value[0],
                    RoleType.doctor.value[0],
                    RoleType.hospital_admin.value[0],
                ],
            ]
        ):
            if (
                user.is_superuser
                or user.role == RoleType.hospital_admin.value[0]
                or MedicalDocument.objects.filter(
                    id=view.kwargs["pk"], uploaded_by_id=user.id
                ).exists()
            ):
                return True
        return False
