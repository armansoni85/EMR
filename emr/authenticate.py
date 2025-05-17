from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import get_user_model
from rest_framework.authentication import BaseAuthentication
from base.utils import success_response
from user.models import CustomUser, TokenBlackList
from base.utils import CustomException, success_response, error_response
from rest_framework.exceptions import APIException
from django.utils.translation import gettext as _
from rest_framework_simplejwt.tokens import AccessToken
from strings import *
from response_codes import *


class PasswordAuthentication(JWTAuthentication):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_model = get_user_model()

    def authenticate(self, request):
        return super().authenticate(request)


class CustomAuthentication(JWTAuthentication):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_model = get_user_model()

    def authenticate(self, request):
        token = None
        auth_header = request.headers.get("Authorization")

        if auth_header and auth_header.startswith("Bearer "):
            token_string = auth_header.split(" ")[1]
            try:
                token = AccessToken(token_string)
            except Exception as e:
                raise APIException(detail=f"{e}")

            user = self.user_model.objects.get(id=token.payload["user_id"])
            if user is not None:
                if not TokenBlackList.objects.filter(
                    user_id=user.id, token=token
                ).exists():
                    if user.change_password == False:
                        return user, token
                    else:
                        raise APIException(
                            detail=_("Please change your password"),
                            code=PASSWORD_CHANGE_NEEDED,
                        )
                else:
                    raise APIException(detail=_("Invalid Token"), code=TOKEN_NOT_VALID)
            else:
                raise APIException(detail=_("Invalid Token"), code=TOKEN_NOT_VALID)

        return super().authenticate(request)
