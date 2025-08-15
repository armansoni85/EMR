from django.contrib import admin
from support.models import AIChatSupport

# Register your models here.
from django.contrib import admin
from support.models import AIChatSupport


@admin.register(AIChatSupport)
class AIChatSupportAdmin(admin.ModelAdmin):
    list_display = ("id", "user__email", "created_at", "short_question")

    def short_question(self, obj):
        return obj.question[:20] + ("..." if len(obj.question) > 20 else "")

    def get_queryset(self, request):
        # Base queryset
        qs = super().get_queryset(request)
        # Optimize query to reduce DB hits
        return qs.select_related("user")
