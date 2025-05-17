from django.contrib import admin
from appointments.models import Appointment


@admin.register(Appointment)
class BookAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related("doctor", "patient").all()
