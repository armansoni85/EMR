from django.shortcuts import render
from base.base_views import (
    CustomViewSetV2,
)
from employee.serializers import (
    ProfessionalInformationSerializer,
    DutyDetailSerializer,
    QualificationSerializer,
    CertificationSerializer,
)
from employee.models import (
    ProfessionalInformation,
    DutyDetail,
    Certification,
    Qualification,
)
from rest_framework.permissions import IsAuthenticated
from employee.permissions import (
    CanCreateEmployee,
    CanUpdateDeleteEmployee,
    CanCreateQualificationDutyDetailCertification,
    CanUpdateDeleteQualification,
    CanUpdateDeleteCertification,
    CanUpdateDeleteDutyDetail,
)
from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter
from employee.filters import (
    ProfessionalInfoFilterSet,
    CertificationFilterSet,
    QualificationFilterSet,
    DutyDetailFilterSet,
)
from user.choices import RoleType



class ProfessionalInformationAPI(CustomViewSetV2):
    """
    This API is to view,create and update the ProfessionalInformation
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = ProfessionalInformationSerializer
    model_class = ProfessionalInformation
    queryset = ProfessionalInformation.objects.select_related("user").all()
    filter_backends = (filters.DjangoFilterBackend, SearchFilter)
    filterset_class = ProfessionalInfoFilterSet

    search_fields = (
        "user__fist_name",
        "profession_id",
        "speciality",
        "sub_speciality",
    )

    def get_queryset(self):
        # only SuperAdmin can all user whereas other user can see on their hospital users only
        qs = super().get_queryset()
        user = self.request.user
        if user.is_anonymous:
            return qs.none()
        if user.is_superuser:
            return qs
        elif user.role == RoleType.hospital_admin.value[0]:
            return qs.filter(user__hospital_id=self.request.user.hospital_id)
        else:
            return qs.filter(user_id=user.id)

    def get_serializer_context(self):
        context = super(ProfessionalInformationAPI, self).get_serializer_context()
        context.update({"request": self.request})
        return context

    def initial(self, request, *args, **kwargs):
        method = request.method
        if method == "POST":
            self.permission_classes = (CanCreateEmployee,)
        elif method in ["PUT", "DELETE"]:
            self.permission_classes = (CanUpdateDeleteEmployee,)
        return super().initial(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        # hospital admin can update any doctor professional info of his hospital
        # hospital employ only can update his/her own professional information
        return super().update(request, *args, **kwargs)


class DutyDetailAPI(CustomViewSetV2):
    """
    This API is to create the DutyDetail
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = DutyDetailSerializer
    model_class = DutyDetail
    queryset = DutyDetail.objects.select_related("user").all()
    filter_backends = (filters.DjangoFilterBackend, SearchFilter)
    filterset_class = DutyDetailFilterSet

    search_fields = (
        "user__fist_name",
        "department_name",
    )

    def get_queryset(self):
        # only SuperAdmin can all user whereas other user can see on their hospital users only
        qs = super().get_queryset()
        user = self.request.user
        if user.is_anonymous:
            return qs.none()
        if user.is_superuser:
            return qs
        elif user.role == RoleType.hospital_admin.value[0]:
            return qs.filter(user__hospital_id=self.request.user.hospital_id)
        else:
            return qs.filter(user_id=user.id)

    def get_serializer_context(self):
        context = super(DutyDetailAPI, self).get_serializer_context()
        context.update({"request": self.request})
        return context

    def initial(self, request, *args, **kwargs):
        method = request.method
        if method == "POST":
            self.permission_classes = (CanCreateQualificationDutyDetailCertification,)
        elif method == "PUT":
            self.permission_classes = (CanUpdateDeleteDutyDetail,)
        return super().initial(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)


class QualificationAPI(CustomViewSetV2):
    """
    This API is to create the Qualification
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = QualificationSerializer
    model_class = Qualification
    queryset = Qualification.objects.select_related("user").all()
    filter_backends = (filters.DjangoFilterBackend, SearchFilter)
    filterset_class = QualificationFilterSet

    search_fields = ("user__fist_name", "name", "description", "organization")

    def get_queryset(self):
        # only SuperAdmin can all user whereas other user can see on their hospital users only
        qs = super().get_queryset()
        user = self.request.user
        if user.is_anonymous:
            return qs.none()
        if user.is_superuser:
            return qs
        elif user.role == RoleType.hospital_admin.value[0]:
            return qs.filter(user__hospital_id=self.request.user.hospital_id)
        else:
            return qs.filter(user_id=user.id)

    def get_serializer_context(self):
        context = super(QualificationAPI, self).get_serializer_context()
        context.update({"request": self.request})
        return context

    def initial(self, request, *args, **kwargs):
        method = request.method
        if method == "POST":
            self.permission_classes = (CanCreateQualificationDutyDetailCertification,)
        elif method == "PUT":
            self.permission_classes = (CanUpdateDeleteQualification,)
        return super().initial(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)


class CertificationsAPI(CustomViewSetV2):
    """
    This API is to create the Hospital
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = CertificationSerializer
    model_class = Certification
    queryset = Certification.objects.select_related("user").all()
    filter_backends = (filters.DjangoFilterBackend, SearchFilter)
    filterset_class = CertificationFilterSet

    search_fields = (
        "user__fist_name",
        "name",
        "issued_by",
    )

    def get_queryset(self):
        # only SuperAdmin can all user whereas other user can see on their hospital users only
        qs = super().get_queryset()
        user = self.request.user
        if user.is_anonymous:
            return qs.none()
        if user.is_superuser:
            return qs
        elif user.role == RoleType.hospital_admin.value[0]:
            return qs.filter(user__hospital_id=self.request.user.hospital_id)
        else:
            return qs.filter(user_id=user.id)

    def get_serializer_context(self):
        context = super(CertificationsAPI, self).get_serializer_context()
        context.update({"request": self.request})
        return context

    def initial(self, request, *args, **kwargs):
        method = request.method
        if method == "POST":
            self.permission_classes = (CanCreateQualificationDutyDetailCertification,)
        elif method == "PUT":
            self.permission_classes = (CanUpdateDeleteCertification,)
        return super().initial(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
