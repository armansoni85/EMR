from base.tasks import *
from base.utils import (
    save_data_into_csv,
    get_epoch_datetime,
    get_yes_no_from_value_presence,
    convert_enum_class_to_dict,
    search_key_on_dict,
)
from api_log.models import APIRequestLog
from report.models import Report
from report.choices import ReportType
from report.tasks import send_report_to_user
from service_provider_apis.authentication.ationet_authentications import (
    get_mqg_admin_token,
)
from service_provider_apis.ationet_log.get_audit_log import get_audit_logs
from base.choices import (
    ATIONETActionOption,
    ATIONETCategoryOptions,
    ATIONETSubCategoryOptions,
)


@app.task()
def download_mqg_api_request_data(report_id):
    """here it will generate the report and then send it to the report task to send the email"""
    report_instance = Report.objects.select_related("user").filter(id=report_id).first()
    context_dict = report_instance.context
    api_request_logs = APIRequestLog.objects.select_related("user").filter(
        id__in=json.loads(context_dict.get("api_request_ids"))
    )

    api_request_log_data = [
        {
            "UserVendorId": api_request_log.user.vendor_user_id
            if api_request_log.user
            else "",
            "User": api_request_log.user.email if api_request_log.user else "",
            "URL": api_request_log.endpoint,
            "Method": api_request_log.method,
            "ResponseCode": api_request_log.response_code,
            "IPAddress": api_request_log.remote_address,
            "Mobile": get_yes_no_from_value_presence(api_request_log.is_mobile),
            "TouchCapable": get_yes_no_from_value_presence(
                api_request_log.is_touch_capable
            ),
            "PC": get_yes_no_from_value_presence(api_request_log.is_pc),
            "Bot": get_yes_no_from_value_presence(api_request_log.is_bot),
            "Browser": api_request_log.browser_family,
            "BrowserVersion": api_request_log.browser_version,
            "OS": api_request_log.os_family,
            "OSVersion": api_request_log.os_version,
            "Device": api_request_log.device_family,
        }
        for api_request_log in api_request_logs
    ]

    report_instance.file_data.save(
        name=f"{ReportType.mqg_log_reports.value[0]}{get_epoch_datetime()}.csv",
        content=save_data_into_csv(data=api_request_log_data),
    )

    send_report_to_user.apply_async(
        kwargs={
            "report_id": str(report_instance.id),
            "user_email": report_instance.user.email,
            "host": report_instance.context["host"],
            "report_requested": len(api_request_logs),
            "report_generated": len(api_request_log_data),
        }
    )

    return {"message": "API Request Log CSV Data Sent to Request user email."}


@app.task()
def download_ationet_api_log_data(report_id):
    """here it will generate the report and then send it to the report task to send the email"""
    report_instance = Report.objects.select_related("user").filter(id=report_id).first()
    context_dict = report_instance.context

    auth_data = {}
    ationet_log_data = []
    total_pages = 1
    current_page = 1
    total_ationet_data_count = 0
    action_dict = convert_enum_class_to_dict(ATIONETActionOption)
    category_dict = convert_enum_class_to_dict(ATIONETCategoryOptions)
    sub_category_dict = convert_enum_class_to_dict(ATIONETSubCategoryOptions)

    while current_page <= total_pages:
        auth_data = get_mqg_admin_token(auth_data=auth_data)
        api_response = get_audit_logs(
            token=auth_data["token"],
            param=context_dict["param"],
        )
        total_ationet_data_count = api_response["TotalCount"]
        for api_request_log in api_response["Content"]:
            ationet_log_data.append(
                {
                    "Id": api_request_log["Id"],
                    "UserId": api_request_log["UserId"],
                    "UserName": api_request_log["UserName"],
                    "Action": search_key_on_dict(
                        dict_value=action_dict,
                        key_to_be_found=str(api_request_log["Action"]),
                    ),
                    "Category": search_key_on_dict(
                        dict_value=category_dict,
                        key_to_be_found=str(api_request_log["Category"]),
                    ),
                    "SubCategory": search_key_on_dict(
                        dict_value=sub_category_dict,
                        key_to_be_found=str(api_request_log["SubCategory"]),
                    ),
                    "NetworkId": api_request_log["NetworkId"],
                    "CompanyId": api_request_log["CompanyId"],
                    "Origin": api_request_log["Origin"],
                    "OriginDescription": api_request_log["OriginDescription"],
                    "OriginDescription": api_request_log["OriginDescription"],
                    "NetworkName": api_request_log["NetworkName"],
                    "CompanyName": api_request_log["CompanyName"],
                    "MerchantName": api_request_log["MerchantName"],
                    "NetworkDate": api_request_log["NetworkDate"],
                    "NetworkDateString": api_request_log["NetworkDateString"],
                    "RealDate": api_request_log["RealDate"],
                    "RealDateString": api_request_log["RealDateString"],
                }
            )

        current_page += 1

    report_instance.file_data.save(
        name=f"{ReportType.ationet_log_reports.value[0]}{get_epoch_datetime()}.csv",
        content=save_data_into_csv(data=ationet_log_data),
    )

    send_report_to_user.apply_async(
        kwargs={
            "report_id": str(report_instance.id),
            "user_email": report_instance.user.email,
            "host": report_instance.context["host"],
            "report_requested": total_ationet_data_count,
            "report_generated": len(ationet_log_data),
        }
    )

    return {"message": "ATIONET API Request Log CSV Data Sent to Request user email."}
