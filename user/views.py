from django.utils.translation import gettext as _
from rest_framework_simplejwt.tokens import RefreshToken, BlacklistMixin
from rest_framework import status
from django.db import transaction
from django.contrib.auth import authenticate
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from rest_framework.filters import SearchFilter
from base.base_views import (
    CustomViewSetV2,
)
from rest_framework.exceptions import APIException
from django.template.loader import render_to_string
from django.db.models import Max
from emr.authenticate import PasswordAuthentication
from .permissions import (
    CanCreateUser,
    CanUpdateUser,
    CanDeleteUser,
)
from .serializers import (
    CustomUserSerializer,
    LoginSerializer,
    UserPasswordUpdateSerializer,
    UserCodeAndTokenSerializer,
    UserPasswordCodeAndTokenSerializer,
    UserListSerializers,
    UserLogoutSerializers,
)
from user.models import CustomUser, TokenBlackList, DeviceToken
from base.utils import get_jwt_auth_token
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import AUTH_HEADER_TYPES
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.backends import TokenBackend, TokenBackendError
from django.conf import settings
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from strings import *
from base.utils import (
    success_response,
    error_response,
    create_otp,
    random_password,
    read_csv_file_with_pandas,
    get_jwt_auth_token,
)
from base.base_views import CustomAPIView

from base.swagger_view import CustomSchemaNoDefaultFilterView

# for swagger
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from drf_yasg.utils import swagger_auto_schema
from django_filters import rest_framework as filters
from user.filters import UserFilterSet
from response_codes import *
from django.utils import timezone
from base.tasks import send_mail_task
from rest_framework.serializers import ValidationError
from base.utils import LoginThrottleRate
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser
from user.choices import RoleType


class LoginView(CustomViewSetV2):
    """
    Returns a MQG token , email & password needed
    Throttle class : LoginThrottleRate , a custom throttle class for the login api
    """

    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer
    throttle_classes = (LoginThrottleRate,)

    def create(self, request, *args, **kwargs):
        # getting the creds from the request
        email = request.data.get("email")
        password = request.data.get("password")

        # getting the user instance using the creds
        user = authenticate(request, email=email, password=password)

        if user:
            user = CustomUser.objects.filter(email=email).first()

        if not user:
            raise APIException(_("User Not Found"), code=status.HTTP_404_NOT_FOUND)

        return self.get_response_for_user(
            user=user,
        )

    def get_response_for_user(self, user):
        # fetch the mqg token from the user
        user_token = get_jwt_auth_token(user=user)
        data = {
            "email": user.email,
            "role": user.role,
            "access": user_token["access"],
            "refresh": user_token["refresh"],
        }

        return self.get_response(
            message=_("Login Successful"), status=status.HTTP_200_OK, data=data
        )


class RefreshTokenView(CustomViewSetV2):
    """
    Return a refresh token
    """

    permission_classes = ()
    authentication_classes = ()
    serializer_class = TokenRefreshSerializer
    www_authenticate_realm = "api"

    def get_authenticate_header(self, request):
        return '{0} realm="{1}"'.format(
            AUTH_HEADER_TYPES[0],
            self.www_authenticate_realm,
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user_data = TokenBackend(
                settings.SIMPLE_JWT["ALGORITHM"], settings.SIMPLE_JWT["SIGNING_KEY"]
            ).decode(serializer.validated_data["access"])
            user = CustomUser.objects.get(id=user_data["user_id"])
            if not user.is_active:
                raise Exception(USER_NOT_ACTIVE)

        except Exception as e:
            raise InvalidToken(str(e))
        return self.get_response(data=serializer.validated_data)


class PasswordTokenVerifyAPI(CustomAPIView):
    """
    Verifies the token and OTP, generates a temporary password, and sends it to the user's email.
    """

    serializer_class = None
    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        request_body=UserCodeAndTokenSerializer
    )  # SerializerFor Swagger
    def post(self, request):
        token = request.data["token"]
        if TokenBlackList.objects.filter(token=token).exists():
            raise ValidationError(_("Token Invalid"))

        user_data = TokenBackend(
            settings.SIMPLE_JWT["ALGORITHM"], settings.SIMPLE_JWT["SIGNING_KEY"]
        ).decode(token)

        if not (
            user_data["otp"] == request.data["otp"]
            or (settings.ENV == "development" and request.data["otp"] == "111111")
        ):
            raise APIException(INVALID_CODE)

        user = CustomUser.objects.get(email__iexact=user_data["email"])

        password = random_password(6)
        CustomUser.objects.filter(email=user_data["email"]).update(
            password=make_password(password), change_password=True
        )

        # black listing the token.
        TokenBlackList.objects.create(user=user, token=token)

        send_mail_task.apply_async(
            kwargs={
                "subject": _("Contraseña temporal"),
                "html_message": render_to_string(
                    "emails/password_reset_temp.html",
                    context={
                        "name": user.get_full_name(),
                        "temp": password,
                    },
                ),
                "recipient_list": [user.email],
            }
        )
        return success_response(message=_("temporary password sent to mail"))


class PasswordTokenVerifyWithNewPassAPI(CustomAPIView):
    """
    Verifies the token and OTP, and update password without old password.
    """

    serializer_class = None
    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        request_body=UserPasswordCodeAndTokenSerializer
    )  # SerializerFor Swagger
    def post(self, request):
        token = request.data["token"]
        if TokenBlackList.objects.filter(token=token).exists():
            raise ValidationError(_("Token Invalid"))

        user_data = TokenBackend(
            settings.SIMPLE_JWT["ALGORITHM"], settings.SIMPLE_JWT["SIGNING_KEY"]
        ).decode(token)

        if not (
            user_data["otp"] == request.data["otp"]
            or (settings.ENV == "development" and request.data["otp"] == "111111")
        ):
            raise APIException(INVALID_CODE)
        CustomUser.objects.filter(email=user_data["email"]).update(
            password=make_password(request.data["password"])
        )
        return success_response(message=_("password successfully reset."))


class PasswordChangeAPI(CustomAPIView):
    """
    GET REQUEST - Sends an OTP and a link to the user's email for password change request.
    PUT REQUEST - Updates the user's password.
    """

    authentication_classes = [PasswordAuthentication]
    serializer_class = None

    def initial(self, request, *args, **kwargs):
        if request.method in ("GET", "POST"):
            self.permission_classes = (AllowAny,)
        super().initial(request, *args, **kwargs)

    email_param = openapi.Parameter(
        "email", openapi.IN_QUERY, description="Enter Email", type=openapi.TYPE_STRING
    )  # defining swagger email param

    @swagger_auto_schema(
        manual_parameters=[email_param],
        auto_schema=CustomSchemaNoDefaultFilterView,
    )  # this for email param in swagger
    def get(self, request):
        user = (
            CustomUser.objects.only("id", "email", "first_name", "last_name")
            .filter(email__iexact=request.query_params["email"])
            .first()
        )

        if user is not None:
            otp = create_otp(6)
            token = TokenBackend(
                settings.SIMPLE_JWT["ALGORITHM"], settings.SIMPLE_JWT["SIGNING_KEY"]
            ).encode(
                {
                    "email": user.email.lower(),
                    "otp": otp,
                    "exp": int(
                        (
                            timezone.now()
                            + timezone.timedelta(
                                # days=settings.RESET_PASSWORD_OTP_EXPIRY_IN_DAYS
                                minutes=settings.RESET_PASSWORD_OTP_EXPIRY_IN_MINS
                            )
                        ).timestamp()
                    ),
                }
            )

            link = f"{settings.FRONTEND_URL}/#/auth/verify-code/{token}"
            # this will redirect to the frontend reset password page

            html_file = (
                "emails/password_reset_otp.html"
                if str(settings.ENV).lower()
                in ["prod", "production", "staging", "stag"]
                else "emails/password_reset_otp_dev.html"
            )
            send_mail_task.apply_async(
                kwargs={
                    "subject": "Recuperación de contraseña",
                    "html_message": render_to_string(
                        html_file,
                        context={
                            "name": user.get_full_name(),
                            "link": link,
                            "email": user.email,
                            "otp": otp,
                            "api_url": settings.API_URL,
                            "otp_expiry_duration": 24
                            * settings.RESET_PASSWORD_OTP_EXPIRY_IN_DAYS,  # 1 day= 24 hours
                            "otp_expiry_duration": settings.RESET_PASSWORD_OTP_EXPIRY_IN_MINS,
                        },
                    ),
                    "recipient_list": [user.email],
                }
            )

            return success_response(message=RESET_PASSWORD_LINK_SENT)
        return error_response(message=EMAIL_NOT_EXISTS)

    @swagger_auto_schema(request_body=UserPasswordUpdateSerializer)
    @transaction.atomic
    def put(self, request):
        user = request.user
        password = request.data["password"]
        if check_password(request.data["password"], request.user.password):
            return error_response(message=SAME_PASSWORD_ERROR)

        CustomUser.objects.filter(id=user.id).update(
            password=make_password(password), change_password=False
        )
        return success_response(message=PASSWORD_UPDATED)


class ProfileAPI(CustomViewSetV2):
    """
    Returns user profile data along with the entities access
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = CustomUserSerializer

    def retrieve(self, request, **kwargs):
        user_data = self.get_serializer(request.user).data
        return self.get_response(
            message=_("Profile fetched successfully"), data=user_data
        )


class UserViewsetAPI(CustomViewSetV2):
    """ """

    permission_classes = (IsAuthenticated,)
    serializer_class = CustomUserSerializer
    model_class = CustomUser
    queryset = CustomUser.objects.all()
    filter_backends = (filters.DjangoFilterBackend, SearchFilter)
    filterset_class = UserFilterSet
    parser_classes = [MultiPartParser]

    search_fields = (
        "email",
        "first_name",
        "last_name",
        "phone_number",
    )

    def get_queryset(self):
        # only SuperAdmin can all user whereas other user can see on their hospital users only
        qs = super().get_queryset()
        if self.kwargs.get("pk"):
            qs = qs.select_related("hospital")
        current_user = self.request.user
        if current_user.is_superuser:
            return qs
        elif current_user.role == RoleType.doctor.value[0]:
            # TODO to make doctor can see only his patients ony. currently doctor can see all patients.
            return qs.filter(
                hospital_id=current_user.hospital_id, role=RoleType.patient.value[0]
            )
        else:
            return qs.filter(hospital_id=current_user.hospital_id, is_superuser=False)

    def get_serializer_context(self):
        context = super(UserViewsetAPI, self).get_serializer_context()
        context.update({"request": self.request})
        return context

    def initial(self, request, *args, **kwargs):
        if request.method == "GET":
            self.serializer_class = UserListSerializers
        if request.method == "POST":
            self.permission_classes = (CanCreateUser,)
        if request.method == "PUT":
            self.permission_classes = (CanUpdateUser,)
        if request.method == "DELETE":
            self.permission_classes = (CanDeleteUser,)
        return super().initial(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.serializer_class = CustomUserSerializer
        return super().retrieve(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class LogoutView(BlacklistMixin, CustomViewSetV2):
    """
    Expires the access token and the refresh token
    """

    permission_classes = [IsAuthenticated]
    serializer_class = UserLogoutSerializers

    @swagger_auto_schema(
        operation_description=_(LOGGED_OUT_DESC),
    )  # this for description of logout in swagger
    def create(self, request):
        try:
            # Additional step: Blacklist the access token
            access_token = request.META.get("HTTP_AUTHORIZATION", "").split(" ")[1]

            # Blacklist the refresh token
            RefreshToken(request.data["refresh"]).blacklist()

            TokenBlackList.objects.create(token=access_token, user_id=request.user.id)
            # deleting registration token for push notification when logout
            # clearing the token
            DeviceToken.objects.filter(
                user_id=request.user.id, session_id=self.request.session._session_key
            ).delete()
            return self.get_response(message=_("Logout success"))
        except Exception as e:
            raise APIException(detail=f"{e}", code=TOKEN_BLACK_LISTED)
