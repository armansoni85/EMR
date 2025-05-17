from base.filters import FilterBaseSet
from hospital.models import Hospital


class HospitalFilterSet(FilterBaseSet):
    class Meta:
        model = Hospital
        fields = ["country", "hospital_type", "speciality", "hospital_rating", "city"]
