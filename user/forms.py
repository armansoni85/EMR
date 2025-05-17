from django import forms
from django.forms import EmailField
from .models import (
    CustomUser,
    # CustomGroup
)
from strings import *
from base.utils import random_password
from django.contrib.auth.models import Permission


# class CustomGroupForm(forms.ModelForm):
#     """
#     A form for creating and updating CustomGroup instances.
#     """

#     def __init__(self, *args, **kwargs):
#         """
#         Initializes the form instance.
#         """
#         super().__init__(*args, **kwargs)
#         # Filter out group permissions and exclude them from the form
#         group_permissions = Permission.objects.filter(codename__in=[
#             'add_group',
#             'change_group',
#             'delete_group',
#             'view_group'
#         ])
#         self.fields['permissions'].queryset = self.fields['permissions'].queryset.exclude(
#             id__in=group_permissions)

#     class Meta:
#         """
#         Meta class specifying the model and fields for the form.
#         """
#         model = CustomGroup
#         fields = '__all__'


class CustomUserCreationForm(forms.ModelForm):
    password = random_password(10)
    host = " "

    class Meta:
        model = CustomUser
        fields = (
            "first_name",
            "last_name",
            "email",
            # "phone_number_1",
            # "phone_number_2",
            "is_superuser",
        )

        field_classes = {"email": EmailField}
