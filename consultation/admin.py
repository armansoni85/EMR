from django.contrib import admin
from .models import Consultation, ConsultationRecording

# Register your models here.
admin.site.register((Consultation, ConsultationRecording))
