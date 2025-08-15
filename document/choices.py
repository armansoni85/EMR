from base.choices import ChoiceEnum


class DepartmentChoices(ChoiceEnum):
    cardiology = ("CARDIOLOGY", "Cardiology")
    neurology = ("NEUROLOGY", "Neurology")
    orthopedics = ("ORTHOPEDICS", "Orthopedics")
    radiology = ("RADIOLOGY", "Radiology")
    general = ("GENERAL", "General")
    other = ("OTHER", "Other")
