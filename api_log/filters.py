from base.filters import filters, FilterBaseSet
from django_filters import rest_framework as filters
from api_log.models import APIRequestLog


class AuditLogAtionetFilterSet(filters.FilterSet):
    userIds = filters.CharFilter(lookup_expr="icontains")
    categories = filters.CharFilter(lookup_expr="icontains")
    dateFrom = filters.CharFilter(lookup_expr="icontains", required=True)
    dateTo = filters.CharFilter(lookup_expr="icontains")
    idCompany = filters.CharFilter(lookup_expr="icontains")
    page = filters.CharFilter(lookup_expr="icontains")
    pageSize = filters.CharFilter(lookup_expr="icontains")
    action = filters.CharFilter(lookup_expr="icontains")
    subCategory = filters.CharFilter(lookup_expr="icontains")
    timeFrom = filters.CharFilter(lookup_expr="icontains")
    timeTo = filters.CharFilter(lookup_expr="icontains")


class APIRequestLogFilterSet(FilterBaseSet):
    class Meta:
        model = APIRequestLog
        fields = [
            "user",
            "method",
            "is_pc",
            "is_tablet",
            "is_mobile",
            "is_touch_capable",
            "response_code",
        ]
