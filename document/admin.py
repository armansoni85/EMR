from django.contrib import admin
from document.models import MedicalDocument


# Register your models here.
@admin.register(MedicalDocument)
class MedicalDocumentAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("uploaded_by", "uploaded_to")

    list_display = ["file_name", "uploaded_by__email", "uploaded_to__email"]
