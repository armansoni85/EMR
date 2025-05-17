from enum import Enum
from django.utils.translation import gettext as _


class ChoiceEnum(Enum):
    @classmethod
    def get_value(cls, member):
        return cls[member].value[0]

    @classmethod
    def get_choices(cls):
        return tuple(x.value for x in cls)

    @classmethod
    def has_value(cls, value):
        return any(value == item.value[0] for item in cls)

    @classmethod
    def get_description(cls, value):
        for item in cls:
            if value == item.value[0]:
                return item.value[1]


class StatusType(ChoiceEnum):
    success = ("success", "Success")
    failed = ("failed", "Failed")
    cancelled = ("cancelled", "Cancelled")
    in_progress = ("in_progress", "In Progress")


class DeactivationChoices(ChoiceEnum):
    client = ("1", "By Client")
    erp = ("2", "By ERP")
    user = ("3", "By user")


class NotificationType(ChoiceEnum):
    tnc_updated = ("TNC", "Terms and conditions updated")
    payment_terms_updated = ("PTU", "Payment terms updated")
    privacy_policy_updated = ("PPU", "Privacy policy updated")
    admin = ("ADMIN", "Sent by admin")


class DeviceType(ChoiceEnum):
    android = ("ANDROID", "android")
    ios = ("IOS", "ios")
    web = ("WEB", "web")


class WeekDay(ChoiceEnum):  # will be used all over the project
    sunday = ("0", _("Sunday"))
    monday = ("1", _("Monday"))
    tuesday = ("2", _("Tuesday"))
    wednesday = ("3", _("Wednesday"))
    thursday = ("4", _("Thursday"))
    friday = ("6", _("Friday"))
    saturday = ("7", _("Saturday"))


class RequestMethod(ChoiceEnum):
    get = ("GET", _("GET"))
    post = ("POST", _("POST"))
    put = ("PUT", _("PUT"))
    delete = ("DELETE", _("DELETE"))
