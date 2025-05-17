from base.choices import ChoiceEnum




class RoleType(ChoiceEnum):
    """This are role types that we have in our system"""
    hospital_admin = ("1", "Hospital Admin")
    doctor = ("2", "Doctor")
    patient = ("3", "Patient")

class GenderType(ChoiceEnum):
    """These are gender type we have in our system"""
    male = ("male", "Male")
    doctor = ("female", "Female")
    other = ("other", "Other")

class PermissionType(ChoiceEnum):
    view=("view","View")
    create=("create","Create")
    delete=("delete","Delete")
    update=("update","Update")