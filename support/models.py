from django.utils.translation import gettext_lazy as _
from django.db import models
from base.base_models import BaseModel
from django.conf import settings


class AIChatSupport(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("User")
    )
    question = models.CharField(max_length=200, verbose_name=_("Question"))
    reply = models.TextField(verbose_name=_("Reply"))

    class Meta:
        ordering = ("-created_at",)
        verbose_name_plural = "AIChatSupport"
        verbose_name = "AIChatSupports"

    def __str__(self):
        return f"{self.question[:10]}"
