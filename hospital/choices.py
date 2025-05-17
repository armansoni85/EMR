from base.choices import ChoiceEnum

class HospitalType(ChoiceEnum):
    general=("GENERAL","General")
    specialized=("SPECIALIZED","Specialized") # Cardiology
    teaching=("TEACHING","Teaching")
    research=("RESEARCH","Research") #Focus on clinical trials and medical research.
    trauma_center=("TRAUMACENTER","Trauma Center") #Specialized in handling severe injuries and critical care
