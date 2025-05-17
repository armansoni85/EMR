from django_filters import rest_framework as filters


class FilterBaseSet(filters.FilterSet):
    created_range = filters.DateFromToRangeFilter(field_name="created_at")
    modified_range = filters.DateFromToRangeFilter(field_name="modified_at")

    ordering = filters.OrderingFilter(
        fields=(("created_at", "created"), ("modified_at", "modified")),
        field_labels={
            "created_at": "date of registrations",
            "modified_at": "date of modification",
        },
    )
