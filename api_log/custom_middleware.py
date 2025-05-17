import time
from base.choices import RequestMethod
import ast
from base.utils import decode_binary_str_to_json
from api_log.models import APIRequestLog
import json
from ipware import get_client_ip


class UserLogHistory:
    """
    This middleware log API Request by user
    """

    CLEANED_SUBSTITUTE = "********************"
    sensitive_fields = {}

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """
        Code to be executed for each request before the view (and later
        middleware) are called.
        """

        # Donot log GET Method
        if request.method == RequestMethod.get.value[0]:
            return self.get_response(request)

        request_body = self._clean_data(request.body)
        _t = time.time()  # Calculated execution time.
        response = self.get_response(request)  # Get response from view function.
        _t = int((time.time() - _t) * 1000)
        # Create instance of our model and assign values
        api_request_log_instance = APIRequestLog(
            endpoint=request.get_full_path(),
            response_code=response.status_code,
            method=request.method,
            remote_address=self.get_client_ip(request),
            exec_time=_t,
            body_request=str(request_body),
        )
        user_agent = request.user_agent
        setattr(api_request_log_instance, "is_mobile", user_agent.is_mobile)
        setattr(
            api_request_log_instance, "is_touch_capable", user_agent.is_touch_capable
        )
        setattr(api_request_log_instance, "is_tablet", user_agent.is_tablet)
        setattr(api_request_log_instance, "is_bot", user_agent.is_bot)
        setattr(
            api_request_log_instance, "is_touch_capable", user_agent.is_touch_capable
        )
        setattr(api_request_log_instance, "is_pc", user_agent.is_pc)
        setattr(api_request_log_instance, "browser_family", user_agent.browser.family)
        setattr(
            api_request_log_instance,
            "browser_version",
            user_agent.browser.version_string,
        )
        setattr(api_request_log_instance, "os_family", user_agent.os.family)
        setattr(api_request_log_instance, "os_version", user_agent.os.version_string)
        setattr(api_request_log_instance, "device_family", user_agent.device.family)

        response_content = decode_binary_str_to_json(response.content)
        if response_content:
            response_content = self._clean_data(response_content.get("data"))
        else:
            response_content = str(response_content)

        setattr(api_request_log_instance, "body_response", str(response_content))

        user = request.user

        if not user.is_anonymous:
            setattr(api_request_log_instance, "user", user)

        # Save log in db
        if not user.is_superuser:
            # we are not logging if activity is performed from admin panel
            # because django admin panel log record itself if performed from admin panel
            try:
                api_request_log_instance.save()

            except Exception as e:
                api_request_log_instance.body_request = (
                    "Payload containing binary file "
                )
                api_request_log_instance.save()

            # send email to the admins.
            from masterdata.models import RecipientAdmin
            from masterdata.choices import ModuleType
            from base.tasks import send_mail_task, render_to_string
            from django.conf import settings
            from rest_framework.status import HTTP_429_TOO_MANY_REQUESTS
            from django.utils import timezone

            if (
                api_request_log_instance.response_code == HTTP_429_TOO_MANY_REQUESTS
                and not APIRequestLog.objects.filter(
                    endpoint=api_request_log_instance.endpoint,
                    response_code=HTTP_429_TOO_MANY_REQUESTS,
                    remote_address=api_request_log_instance.remote_address,
                    user=api_request_log_instance.user,
                    method=api_request_log_instance.method,
                    created_at__gte=timezone.now() - timezone.timedelta(minutes=3),
                )
                .exclude(id=api_request_log_instance.id)
                .exists()
            ):
                admin_lists = list(
                    RecipientAdmin.objects.filter(
                        module=ModuleType.SUSPICIOUS_ACTIVITY.value[0]
                    ).values_list("user__email", flat=True)
                )

                send_mail_task.apply_async(
                    kwargs={
                        "subject": "Actividades sospechosas",
                        "html_message": render_to_string(
                            "emails/suspicious_activity.html",
                            context={
                                "user_email": user.email
                                if user and not user.is_anonymous
                                else None,
                                "endpoint": api_request_log_instance.endpoint,
                                "ip": api_request_log_instance.remote_address,
                                "api_url": settings.API_URL,
                            },
                        ),
                        "recipient_list": [settings.SECURITY_ADMIN]
                        if not admin_lists
                        else admin_lists,
                    }
                )

        return response

    # get clients ip address
    def get_client_ip(self, request):
        client_ip, is_routable = get_client_ip(request)
        return client_ip

    def _clean_data(self, data):
        """
        This hide sensitive data from being logged due to security potential
        """
        if isinstance(data, bytes):
            data = data.decode(errors="replace")
            if 'name="password"' in data:  # if data submitted via form method
                # masking password for security purpose
                return data.split('name="password"')[0]

            if isinstance(data, str):
                try:
                    # it able to load into python list or dict if that is '[]' or '{}'
                    data = json.loads(data)
                except Exception as e:
                    data = data  # error on loading if data is string itself

        if isinstance(data, list):
            return [self._clean_data(d) for d in data]

        if isinstance(data, dict):
            SENSITIVE_FIELDS = {
                "access",
                "refresh",
                "fmc_registration_token",
                "key",
                "secret",
                "password",
                "signature",
            }

            data = dict(data)
            if self.sensitive_fields:
                SENSITIVE_FIELDS = SENSITIVE_FIELDS | {
                    field.lower() for field in self.sensitive_fields
                }

            for key, value in data.items():
                try:
                    value = ast.literal_eval(value)
                except (ValueError, SyntaxError):
                    pass
                if isinstance(value, list) or isinstance(value, dict):
                    data[key] = self._clean_data(value)
                if key.lower() in SENSITIVE_FIELDS:
                    data[key] = self.CLEANED_SUBSTITUTE

        return data

    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Called just before Django calls the view.
        """
        return None

    def process_exception(self, request, exception):
        """
        Called when a view raises an exception.
        """
        return None

    def process_template_response(self, request, response):
        """
        Called just after the view has finished executing.
        """
        return response
