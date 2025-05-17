from django.shortcuts import render
from base.base_views import CustomViewSetAtionet, CustomAPIView, CustomViewSetV2
from service_provider_apis.authentication.ationet_authentications import (
    get_user_access_token_from_ationet,
)
from rest_framework.filters import SearchFilter
from django_filters import rest_framework as filters
from api_log.permissions import (
    CanReadAuditLogs,
    CanDownloadMQGLogs,
    CanReadMQGLogs,
    CanDownloadATIONETAPILogs,
)
from api_log.filters import AuditLogAtionetFilterSet, APIRequestLogFilterSet
import json
from api_log.models import APIRequestLog
from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from report.models import Report
from report.choices import ReportType
from user.tasks import download_user_data
from base.utils import (
    get_host,
    is_current_user_mqg_user,
    generate_ref_id_for_report,
    extract_id_as_str_from_instances,
    success_response,
)
from user.choices import MQGADMINUSERS
from strings import EMPTY_MQG_API_LOG_DATA, DOWNLOAD_REQUEST_SUCCESS
from api_log.tasks import download_mqg_api_request_data, download_ationet_api_log_data
from api_log.serializers import (
    APIRequestLogSerializer,
    DownloadATIONETAPILogSerializers,
)
from base.base_serializers import ReportDownloadSearchSerializer
from rest_framework.parsers import JSONParser


# Create your views here.
class AuditLogAtionetAPIView(CustomViewSetAtionet):
    filterset_class = AuditLogAtionetFilterSet
    permission_classes = (CanReadAuditLogs,)
    http_method_names = ["get", "options", "head"]

    def list(self, request, *args, **kwargs):
        user_entity = self.get_max_role_from_entity(
            user_id=request.user.id,
        )
        if user_entity:
            token = get_user_access_token_from_ationet(user_entity_instance=user_entity)
            response_data = self.get_logs_from_ationet(request=request, token=token)
            return self.get_response(data=response_data)
        return self.get_response()

    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.pop(self.field_pk)
        user_entity = self.get_max_role_from_entity(
            user_id=request.user.id,
        )
        if user_entity:
            token = get_user_access_token_from_ationet(user_entity_instance=user_entity)
            response_data = self.get_logs_from_ationet(
                request=request, token=token, pk=pk
            )
            return self.get_response(data=response_data)
        return self.get_response()

    def get_logs_from_ationet(self, request, token, **kwargs):
        return super(AuditLogAtionetAPIView, self).get_data_from_ationet(
            request, token, endpoint="AuditLog", **kwargs
        )


class APIRequestLogAPIView(CustomViewSetV2):
    serializer_class = APIRequestLogSerializer
    model_class = APIRequestLog
    queryset = APIRequestLog.objects.all()
    filter_backends = (filters.DjangoFilterBackend, SearchFilter)
    filterset_class = APIRequestLogFilterSet
    permission_classes = (CanReadMQGLogs,)
    search_fields = (
        "remote_address",
        "os_family",
        "os_version",
        "browser_family",
        "browser_version",
        "device_family",
        "endpoint",
    )

    def get_queryset(self):
        base_queryset = super().get_queryset().prefetch_related("user")
        if not any([x in MQGADMINUSERS for x in self.request.user.roles]):
            base_queryset = base_queryset.filter(
                Q(user_id=self.request.user.id) | Q(user_id=None)
            )

        return base_queryset


class DownloadMQGAPILogView(CustomAPIView):
    permission_classes = (CanDownloadMQGLogs,)
    serializer_class = None
    parser_classes = [JSONParser]

    @swagger_auto_schema(
        request_body=ReportDownloadSearchSerializer
    )  # SerializerFor Swagger
    def post(self, request, *args, **kwargs):
        """
        1. MQG Admin,MQG Supervisor,Company Admin,Company Supervisor,Merchant Admin users can Download MQG log
        2. Since login request does not have user,so log having user=None can be downloaded by all.
        3. Available choices:is_all,specific_ids,search_query(user_name,ip_address)
        """

        csv_file_download_serializer = ReportDownloadSearchSerializer(data=request.data)
        if csv_file_download_serializer.is_valid(raise_exception=True):
            data = csv_file_download_serializer.data

        search_query = data.get("search_query")
        user = request.user
        specific_ids = data.get("specific_ids", [])
        api_request_log_instances = APIRequestLog.objects.all()
        if not any([x in MQGADMINUSERS for x in user.roles]):
            api_request_log_instances = api_request_log_instances.filter(
                Q(user_id=user.id) | Q(user_id=None)
            )

        if specific_ids:
            api_request_log_instances = api_request_log_instances.filter(
                id__in=specific_ids
            )

        if search_query:
            api_request_log_instances = api_request_log_instances.filter(
                Q(user__email__icontains=search_query)
                | Q(remote_address__icontains=search_query)
            )

        api_request_ids = extract_id_as_str_from_instances(
            instances_list=api_request_log_instances,
            empty_message=EMPTY_MQG_API_LOG_DATA,
        )

        report_instance = Report.objects.create(
            context={
                "host": get_host(request=request),
                "api_request_ids": json.dumps(api_request_ids),
            },
            user_id=user.id,
            report_type=ReportType.mqg_log_reports.value[0],
            ref_id=generate_ref_id_for_report(),
        )

        download_mqg_api_request_data.apply_async(
            kwargs={"report_id": str(report_instance.id)}
        )

        return success_response(
            message=DOWNLOAD_REQUEST_SUCCESS.format(report_instance.ref_id)
        )


class DownloadATIONETAPILogView(CustomAPIView):
    permission_classes = (CanDownloadATIONETAPILogs,)
    serializer_class = None

    @swagger_auto_schema(
        request_body=DownloadATIONETAPILogSerializers
    )  # SerializerFor Swagger
    def post(self, request, *args, **kwargs):
        """
        1. MQG users can Download ATIONET log
        2. Since login request does not have user,so log having user=None can be downloaded by all.
        3. Available choices:specific_date(required),action,category,sub_category,company_id,user_id
        4. Taking single user_id and category in order to avoid getting multiple data

        """

        csv_file_download_serializer = DownloadATIONETAPILogSerializers(
            data=request.data
        )
        if csv_file_download_serializer.is_valid(raise_exception=True):
            data = csv_file_download_serializer.data

        # prepare param
        default_param = f"dateFrom={data['specific_date'].replace('-', '/')}"
        # check if action is passed
        if data.get("action"):
            default_param = default_param + f"&Action={data['action']}"

        if data.get("category"):
            default_param = default_param + f"&categories={data['category']}"

        if data.get("sub_category"):
            default_param = default_param + f"&subCategory={data['sub_category']}"

        if data.get("company_id"):
            default_param = default_param + f"&idCompany={data['company_id']}"

        if data.get("user_id"):
            default_param = default_param + f"&userIds[0]={data['user_id']}"

        report_instance = Report.objects.create(
            context={
                "host": get_host(request=request),
                "param": default_param,
            },
            user_id=request.user.id,
            report_type=ReportType.ationet_log_reports.value[0],
            ref_id=generate_ref_id_for_report(),
        )

        download_ationet_api_log_data.apply_async(
            kwargs={"report_id": str(report_instance.id)}
        )

        return success_response(
            message=DOWNLOAD_REQUEST_SUCCESS.format(report_instance.ref_id)
        )
