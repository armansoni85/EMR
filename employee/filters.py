from base.filters import FilterBaseSet, filters
from employee.models import (
    ProfessionalInformation,
    Qualification,
    DutyDetail,
    Certification,
)


class ProfessionalInfoFilterSet(FilterBaseSet):
    experience_lte = filters.CharFilter(method="filter_exp_lte_x")
    experience_gte = filters.CharFilter(method="filter_exp_gte_x")

    def filter_exp_lte_x(self, queryset, name, value):
        return queryset.filter(years_of_experience__lte=value)

    def filter_exp_gte_x(self, queryset, name, value):
        return queryset.filter(years_of_experience__gte=value)

    class Meta:
        model = ProfessionalInformation
        fields = [
            "speciality",
            "experience_lte",
            "experience_gte",
        ]


class QualificationFilterSet(FilterBaseSet):
    class Meta:
        model = Qualification
        fields = [
            "user",
            "organization",
        ]


class DutyDetailFilterSet(FilterBaseSet):
    class Meta:
        model = DutyDetail
        fields = [
            "user",
            "is_on_call",
            "room_number",
        ]


class CertificationFilterSet(FilterBaseSet):
    class Meta:
        model = Certification
        fields = [
            "user",
            "valid_until",
        ]
