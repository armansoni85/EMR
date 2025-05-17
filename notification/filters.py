from base.filters import FilterBaseSet
from .models import NotificationSent


class NotificationFilterSet(FilterBaseSet):
    class Meta:
        model = NotificationSent
        fields = ["is_notification_seen"]
