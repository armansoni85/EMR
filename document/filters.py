from base.filters import FilterBaseSet
from document.models import MedicalDocument


class MedicalDocumentFilterSet(FilterBaseSet):
    class Meta:
        model = MedicalDocument
        fields = ["belonging_department", "uploaded_by", "uploaded_to"]
