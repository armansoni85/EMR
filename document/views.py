from django.db.models import Q
from base.base_views import (
    CustomViewSetV2,
)
from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter
from document.filters import MedicalDocumentFilterSet
from document.models import MedicalDocument
from document.permissions import (
    CanUploadMedicalDocument,
    CanUpdateDeleteMedicalDocument,
)
from document.serializers import MedicalDocumentSerializer
from user.choices import RoleType


class MedicalDocumentAPI(CustomViewSetV2):
    model = MedicalDocument
    queryset = MedicalDocument.objects.select_related(
        "uploaded_by", "uploaded_to"
    ).all()
    permission_classes = (CanUploadMedicalDocument,)
    serializer_class = MedicalDocumentSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter)
    filterset_class = MedicalDocumentFilterSet
    search_fields = (
        "file_name",
        "note",
    )

    def get_queryset(self):
        qs = super().get_queryset()
        current_user = self.request.user
        if current_user.is_superuser:
            # superuser can see all data
            return qs
        if current_user.role == RoleType.hospital_admin.value[0]:
            # hospital admin can see all data of his/her hospital
            return qs.filter(
                Q(uploaded_to__hospital_id=current_user.hospital_id)
                | Q(uploaded_by__hospital_id=current_user.hospital_id)
            )
        # other user can only see their own documents which are uploaded by them
        return qs.filter(
            Q(uploaded_by_id=current_user.id) | Q(uploaded_to_id=current_user.id)
        )

    def initial(self, request, *args, **kwargs):
        if request.method in ["PUT", "DELETE"]:
            self.permission_classes = (CanUpdateDeleteMedicalDocument,)
        return super().initial(request, *args, **kwargs)

    def get_serializer_context(self):
        context = super(MedicalDocumentAPI, self).get_serializer_context()
        context.update({"request": self.request})
        return context

    def get(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
