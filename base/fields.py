from django.contrib.postgres.fields import ArrayField, JSONField
from django import forms
from django.db import models


class ChoiceArrayField(ArrayField):
    def formfield(self, **kwargs):
        defaults = {
            "form_class": forms.MultipleChoiceField,
            "choices": self.base_field.choices,
        }
        defaults.update(kwargs)
        return super(ArrayField, self).formfield(**defaults)


class ArrayOfDictsField(models.JSONField):
    def formfield(self, **kwargs):
        # Add any custom formfield settings if needed
        return super().formfield(**kwargs)
