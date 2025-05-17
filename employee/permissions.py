from rest_framework.permissions import BasePermission
from user.models import CustomUser
from user.choices import RoleType
from employee.models import Qualification, DutyDetail, Certification


class CanCreateEmployee(BasePermission):
    """Checking if user can create ,delete employee"""

    def has_permission(self, request, view):
        user = request.user
        if user.is_authenticated:
            if user.is_superuser:
                return True
            if (
                user.role == RoleType.hospital_admin.value[0]
                and user.hospital_id == request.data["hospital"]
            ):
                # hospital admin can create employee for his hospital only
                return True
        return False


class CanUpdateDeleteEmployee(BasePermission):
    """Checking if user can update employee or not."""

    def has_permission(self, request, view):
        user = request.user
        if user.is_authenticated and user.is_superuser:
            return True
        # check if user's role is hospital_admin then can updates its own data only
        if user.role == RoleType.hospital_admin.value[0] and view.kwargs["pk"] == str(
            user.hospital_id
        ):
            return True
        return False


class CanCreateQualificationDutyDetailCertification(BasePermission):
    """Checking if user can create qualification,duty-detail and certification or not."""

    def has_permission(self, request, view):
        user = request.user
        if user.is_authenticated:
            if user.is_superuser:
                return True
            if user.role in [
                RoleType.hospital_admin.value[0],
                RoleType.doctor.value[0],
            ]:
                # only own hospital's doctor's qualification,certification and duty-detail can be created
                user_qs = CustomUser.objects.filter(
                    id=request.data["user"], role=RoleType.doctor.value[0]
                ).first()
                if user_qs.hospital_id == user.hospital_id:
                    return True
        return False


class CanUpdateDeleteQualification(BasePermission):
    """Checking if user can update,delete qualification or not."""

    def has_permission(self, request, view):
        user = request.user
        if user.is_authenticated:
            return True
        qualification_qs = (
            Qualification.objects.filter(id=view.kwargs["pk"])
            .select_related("user")
            .first()
        )
        if (
            user.role == RoleType.hospital_admin.value[0]
            and qualification_qs.user.hospital_id == user.hospital_id
        ):
            # hospital admin can update,delete his own hospital's qualification only
            return True
        if user.role == RoleType.doctor.value[0]:
            # doctor can update,delete his own qualification only
            if qualification_qs.user_id == user.id:
                return True
        return False


class CanUpdateDeleteDutyDetail(BasePermission):
    """Checking if user can update,delete update or not."""

    def has_permission(self, request, view):
        user = request.user
        if user.is_authenticated:
            return True

        duty_detail_qs = (
            DutyDetail.objects.filter(user_id=user.id, id=view.kwargs["pk"])
            .select_related("user")
            .first()
        )
        if (
            user.role == RoleType.hospital_admin.value[0]
            and duty_detail_qs.user.hospital_id == user.hospital_id
        ):
            # hospital admin can update,delete his own hospital's qualification only
            return True
        if user.role == RoleType.doctor.value[0]:
            # doctor can update,delete his own qualification only
            if duty_detail_qs.user_id == user.id:
                return True
        return False


class CanUpdateDeleteCertification(BasePermission):
    """Checking if user can update,delete update or not."""

    def has_permission(self, request, view):
        user = request.user
        if user.is_authenticated:
            return True

        duty_detail_qs = (
            Certification.objects.filter(user_id=user.id, id=view.kwargs["pk"])
            .select_related("user")
            .first()
        )
        if (
            user.role == RoleType.hospital_admin.value[0]
            and duty_detail_qs.user.hospital_id == user.hospital_id
        ):
            # hospital admin can update,delete his own hospital's certification only
            return True
        if user.role == RoleType.doctor.value[0]:
            # doctor can update,delete his own certification only
            if duty_detail_qs.user_id == user.id:
                return True
        return False
