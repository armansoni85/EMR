from django.contrib import admin
from employee.models import ProfessionalInformation,DutyDetail,Certification,Qualification
# Register your models here.
admin.site.register((ProfessionalInformation,DutyDetail,Certification,Qualification))