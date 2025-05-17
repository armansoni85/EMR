from base.filters import FilterBaseSet, filters
from user.models import CustomUser


class UserFilterSet(FilterBaseSet):
    class Meta:
        model = CustomUser
        fields = [
            "role",
            "is_blocked",
        ]
