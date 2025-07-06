from django.db import models

class ICDCode(models.Model):
    code = models.CharField(max_length=10, primary_key=True)
    description = models.CharField(max_length=255)

    class Meta:
        verbose_name = "ICD Code"
        verbose_name_plural = "ICD Codes"
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} — {self.description}"


class CPTCode(models.Model):
    code = models.CharField(max_length=10, primary_key=True)
    description = models.CharField(max_length=255)

    class Meta:
        verbose_name = "CPT Code"
        verbose_name_plural = "CPT Codes"
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} — {self.description}"

