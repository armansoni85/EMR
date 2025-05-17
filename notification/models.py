from django.db import models
from user.models import BaseModel, CustomUser
from notification.choices import NotificationType
from base.choices import DeviceType
from django.utils.translation import gettext as _


# Create your models here.
class NotificationSent(BaseModel):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name=_("User"),
    )
    notification_type = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        choices=[x.value for x in NotificationType],
        verbose_name=_("Notification Type"),
    )
    device_type = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        choices=[x.value for x in DeviceType],
        verbose_name=_("Device Type"),
    )
    title = models.CharField(
        max_length=200, null=True, blank=True, verbose_name=_("Title")
    )
    body = models.CharField(max_length=500, verbose_name=_("Body"))
    is_notification_seen = models.BooleanField(
        verbose_name=_("Is Notification Seen"), default=False
    )
    is_sent = models.BooleanField(default=False, verbose_name=_("Is Sent"))
    fmc_registration_token = models.TextField(
        verbose_name=_("FMC Registration Token"), null=True, blank=True
    )

    class Meta:
        ordering = ("-created_at",)
        verbose_name_plural = "Notification"
        verbose_name = "Notifications"

    def __str__(self) -> str:
        return f"{self.id}"
