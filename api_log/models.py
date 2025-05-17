from django.db import models
from base.base_models import BaseModel
from user.models import CustomUser
from base.choices import RequestMethod
from django.utils.translation import gettext as _


# Create your models here.
class APIRequestLog(BaseModel):
    endpoint = models.CharField(
        max_length=100, null=True, verbose_name=_("EndPoint")
    )  # The url the user requested
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_("User"),
        related_name="api_request_logs",
    )  # User that made request, if authenticated
    response_code = models.PositiveSmallIntegerField(
        verbose_name=_("Response Code")
    )  # Response status code
    method = models.CharField(
        max_length=10,
        choices=[x.value for x in RequestMethod],
        null=True,
        verbose_name=_("Method"),
    )  # Request method
    remote_address = models.GenericIPAddressField(
        null=True, verbose_name=_("IP Address")
    )  # IP address of user
    exec_time = models.IntegerField(
        null=True, verbose_name=_("Execution Time In Millisecond")
    )  # Time taken to create the response
    body_response = models.TextField(verbose_name=_("Body Response"))  # Response data
    body_request = models.TextField(verbose_name=_("Body Request"))  # Request data
    is_mobile = models.BooleanField(default=False, verbose_name=_("Is Mobile"))
    is_touch_capable = models.BooleanField(
        default=False, verbose_name=_("Is Touch Capable")
    )
    is_tablet = models.BooleanField(default=False, verbose_name=_("Is Tablet"))
    is_pc = models.BooleanField(default=False, verbose_name=_("Is PC"))
    is_bot = models.BooleanField(default=False, verbose_name=_("Is Bot"))
    browser_family = models.CharField(
        max_length=150, null=True, blank=True, verbose_name=_("Browser Name")
    )
    browser_version = models.CharField(
        max_length=50, verbose_name=_("Browser OS"), null=True, blank=True
    )
    os_family = models.CharField(
        max_length=150, verbose_name=_("OS Family"), null=True, blank=True
    )
    os_version = models.CharField(
        max_length=50, verbose_name=_("OS Version"), null=True, blank=True
    )
    device_family = models.CharField(
        max_length=150, verbose_name=_("Device"), null=True, blank=True
    )

    class Meta:
        ordering = ("-created_at",)
        verbose_name_plural = "API Log"
        verbose_name = "API Logs"

    def __str__(self) -> str:
        return f"{self.endpoint}-{self.response_code}"
