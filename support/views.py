from base.base_views import (
    CustomViewSetV2,
)
from rest_framework.permissions import IsAuthenticated
from support.serializers import AIChatSupportSerializer
from support.models import AIChatSupport
from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter
from user.choices import RoleType
from support.filters import AIChatSupportFilterSet


class AIChatSupportView(CustomViewSetV2):
    model = AIChatSupport
    queryset = AIChatSupport.objects.all()
    serializer_class = AIChatSupportSerializer
    permission_classes = (IsAuthenticated,)

    filter_backends = (filters.DjangoFilterBackend, SearchFilter)
    filterset_class = AIChatSupportFilterSet

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_superuser:
            return qs
        if self.request.user.role == RoleType.hospital_admin:
            return qs.filter(user__hospital_id=self.request.user.hospital_id)

        return qs.filter(user_id=self.request.user.id)

    def get_serializer_context(self):
        context = super(AIChatSupportView, self).get_serializer_context()
        context.update({"request": self.request})
        return context

    def get(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
