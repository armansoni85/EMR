from base.base_views import CustomViewSetV2
from notification.serializers import (
    EnableDisableNotificationSerializer,
    NotificationSerializer,
)
from notification.models import NotificationSent
from user.models import CustomUser
from rest_framework.permissions import IsAuthenticated
from notification.filters import NotificationFilterSet
from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter


class EnableDisableNotificationView(CustomViewSetV2):
    serializer_class = EnableDisableNotificationSerializer
    model_class = CustomUser
    queryset = CustomUser.objects.all()

    permission_classes = (IsAuthenticated,)  # Read permission same as vehicle

    def get_queryset(self):
        return super().get_queryset().filter(id=self.request.user.id)


class NotificationView(CustomViewSetV2):
    serializer_class = NotificationSerializer
    model_class = NotificationSent
    queryset = NotificationSent.objects.all()
    filter_backends = (filters.DjangoFilterBackend, SearchFilter)
    filterset_class = NotificationFilterSet
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return super().get_queryset().filter(user_id=self.request.user.id)
