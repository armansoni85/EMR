from .base_settings import *

SIMPLE_JWT = {
    # TODO: UPDATE THIS IN THE PRODUCTION
    # TODO set it to 1 day
    "ACCESS_TOKEN_LIFETIME": datetime.timedelta(days=60),
    # TODO set it to 30 days
    "REFRESH_TOKEN_LIFETIME": datetime.timedelta(days=120),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": None,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "JTI_CLAIM": "jti",
    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": datetime.timedelta(minutes=5),
    "SLIDING_TOKEN_REFRESH_LIFETIME": datetime.timedelta(days=1),
}


DATA_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024 * 10
