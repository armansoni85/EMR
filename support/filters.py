from base.filters import FilterBaseSet, filters
from support.models import AIChatSupport


class AIChatSupportFilterSet(FilterBaseSet):
    user_email = filters.CharFilter(method="filter_user_email")

    def filter_user_email(self, queryset, name, value):
        return queryset.select_related("user").filter(user__email__icontains=value)

    class Meta:
        model = AIChatSupport
        fields = []
