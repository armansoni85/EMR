import uuid
from django.db.models import Q, UniqueConstraint
from django.db.models.query import QuerySet
from django.utils.translation import gettext as _
from django.db import models
from ckeditor.fields import RichTextField
from django.contrib.auth.models import (
    AbstractUser,
    UserManager,
)
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from base.fields import ChoiceArrayField
from django.db.models import JSONField
from django_countries.fields import CountryField

from strings import *
from base.base_models import ModelDiffMixin, BaseModel, SoftDeletionManager
from base.choices import (
    DeviceType,
)
from base.base_upload_handlers import (
    handle_user_profile_picture,
    handle_image_upload_limit,
)
from base.utils import delete_media
from .choices import (
    RoleType,
    GenderType,
    PermissionType,
)
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from hospital.models import Hospital


class CustomUserManager(UserManager):
    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        """
        Creates a new user with the given email and password.

        Parameters:
            email (str): The email address of the user. Defaults to None.
            password (str): The password of the user. Defaults to None.
            **extra_fields (dict): Additional fields to include in the user object. Defaults to an empty dictionary.

        Returns:
            User: The newly created user object.
        """
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """
        Create a superuser with the given email and password.

        Parameters:
            email (str): The email address of the superuser.
            password (str): The password of the superuser.
            **extra_fields (kwargs): Additional fields to be passed to the _create_user method.

        Raises:
            ValueError: If the is_staff value in extra_fields is not True.
            ValueError: If the is_superuser value in extra_fields is not True.

        Returns:
            User: The created superuser instance.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", [RoleType.hospital_admin.value[0]])

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    username = None
    email = models.EmailField(
        error_messages={"unique": _("A user with that email already exists")},
        unique=True,
        db_index=True,
    )
    created_by = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="users_created_by_me",
    )
    country = CountryField(null=True, blank=True)  # pip install django-countries
    work_email = models.EmailField(null=True, blank=True, verbose_name=_("Work Email"))
    profile_picture = models.ImageField(
        validators=[handle_image_upload_limit],
        upload_to=handle_user_profile_picture,
        verbose_name=_("Profile Picture"),
        null=True,
        blank=True,
    )
    phone_number = models.CharField(
        max_length=50, null=True, blank=True, verbose_name=_("Phone Number")
    )
    address = models.TextField(
        max_length=200, verbose_name=_("Address"), blank=True, null=True
    )
    gender = models.CharField(
        max_length=50, choices=[x.value for x in GenderType], null=True, blank=True
    )
    role = models.CharField(
        max_length=500, choices=[x.value for x in RoleType], null=True, blank=True
    )
    dob = models.DateField(
        help_text="Date of Birth",
        verbose_name=_("Date of Birth"),
        null=True,
        blank=True,
    )
    hospital = models.ForeignKey(
        Hospital,
        on_delete=models.CASCADE,
        related_name="users",
        verbose_name=_("Hospital"),
        null=True,
        blank=True,
    )  # this will be used for access-control
    notification_setting = models.BooleanField(default=True)
    unread_notification_count = models.PositiveIntegerField(default=0)
    is_mobile_push_notification_enable = models.BooleanField(
        default=True,
        null=True,
        blank=True,
        verbose_name=_("Is Mobile Push Notification Enable"),
    )
    is_web_push_notification_enable = models.BooleanField(
        default=True,
        null=True,
        blank=True,
        verbose_name=_("Is Web Push Notification Enable"),
    )
    is_email_notification_enable = models.BooleanField(
        default=True,
        null=True,
        blank=True,
        verbose_name=_("Is Email Notification Enable"),
    )
    # login block on multiple wrong attempt
    login_attempts_failed_count = models.PositiveIntegerField(
        default=0, verbose_name=_("Login Attempt Failed Count")
    )
    last_login_failed_at = models.DateTimeField(
        null=True, blank=True, verbose_name=_("Last Login Failure Datetime")
    )
    auto_unblock_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("User will be able to login after this time"),
        help_text="User can retry to login after this time",
    )
    is_blocked = models.BooleanField(
        default=False,
        verbose_name=_("Is Blocked"),
        help_text=(
            "On multiple retry exceeded ,then user will be blocked for x hour ."
        ),
    )
    change_password = models.BooleanField(
        default=False, verbose_name=_("Change Password")
    )
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def save(self, *args, **kwargs):
        """
        Save the object to the database.

        Parameters:
            *args (tuple): Variable length argument list.
            **kwargs (dict): Arbitrary keyword arguments.

        Raises:
            ValidationError: If the mobile number already exists for another user.

        Returns:
            None
        """
        super().save(*args, **kwargs)

    def validate_unique(self, exclude=None):
        """
        Validate the uniqueness of the instance, optionally excluding specified instances.

        Args:
            exclude (list, optional): A list of instances to exclude from the uniqueness check. Defaults to None.

        Returns:
            None
        """

        if not self.email.islower():
            self.email = self.email.lower()
        super().validate_unique(exclude=["id"])

    class Meta:
        ordering = ("-date_joined",)
        constraints = [
            UniqueConstraint(
                fields=["email"], condition=Q(is_active=False), name="email"
            )
        ]

    def delete(self, *args, **kwargs):
        # once queryset is deleted, delete the document image from the storage
        if self.profile_picture:
            delete_media(self.profile_picture.name)
        super().delete(*args, **kwargs)


class DeviceToken(BaseModel):
    """session_id is used to clear device token logout and
    jwt_refresh_token_expiry_timestamp is used for clearing device_tokens whose refresh token has been expired
    """

    device_type = models.CharField(
        max_length=10,
        choices=[x.value for x in DeviceType],
        verbose_name=_("Device Type"),
    )
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="device_tokens"
    )
    token = models.TextField(verbose_name=_("Token"), unique=True)
    session_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("Session Id"),
        help_text="It helps to uniquely identify device",
    )
    jwt_refresh_token_expiry_timestamp = models.FloatField(
        null=True, blank=True, verbose_name=_("JWT Refresh Token Expiry Timestamp")
    )

    def __str__(self):
        return f"{self.session_id}"

    class Meta:
        ordering = ("-created_at",)
        verbose_name_plural = "Device Tokens"
        verbose_name = "Device Token"


class TokenBlackList(BaseModel):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
    )
    token = models.TextField(max_length=1200, null=True, blank=True)

    def __str__(self):
        return self.user.email

    class Meta:
        ordering = ("-created_at",)
        verbose_name_plural = "Token Blacklist"
        verbose_name = "Token Blacklist"


class UserLoginSession(BaseModel):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="user_login_sessions",
        verbose_name=("User"),
    )
    session_id = models.CharField(max_length=100, verbose_name=("Session Id"))
    session_expired_at = models.DateTimeField(verbose_name=("Session Expiry Datetime"))
    remote_address = models.GenericIPAddressField(
        null=True, blank=True, verbose_name=("Remote Address")
    )

    def __str__(self):
        return f"{self.session_id}"

    class Meta:
        ordering = ("-created_at",)
        verbose_name_plural = "User Login Session"
        verbose_name = "User Login Sessions"


class PasswordResetToken(BaseModel):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name="password_reset_tokens"
    )  # with OneToOne user can use re-use past token ,which is not even used
    token = models.CharField(max_length=250, null=True, blank=True)
    token_expiry_timestamp = models.IntegerField(null=True, blank=True)
    is_token_used = models.BooleanField(default=False)

    class Meta:
        ordering = ("-created_at",)
        verbose_name_plural = "Password Reset Token"
        verbose_name = "Password Reset Tokens"


class UserPermission(BaseModel):
    # this is for controlling permission on user level
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="permissions"
    )
    permission_name = models.CharField(
        max_length=100, verbose_name=_("Permission Name")
    )
    permission_type = models.CharField(
        max_length=50,
        choices=[x.value for x in PermissionType],
        verbose_name=_("Permission Type"),
    )
    # This will store the ContentType of the related model
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, verbose_name=_("Related Model")
    )
    # This will store the primary key of the related model instance
    object_id = models.PositiveIntegerField(
        default=0
    )  # default 0 general permission i.e to all objects of Model, we can specific id as well to specific instance only
    # This creates the GenericForeignKey, linking the above fields
    associated_model = GenericForeignKey(
        "content_type", "object_id"
    )  # it will not be shown in admin panel
    is_active = models.BooleanField(default=True, verbose_name=_("Status"))

    class Meta:
        ordering = ("-created_at",)
        verbose_name_plural = "User Permissions"
        verbose_name = "User Permission"

    def __str__(self):
        return self.permission_type

    @staticmethod
    def has_permission(self, user, obj, permission_type):
        return UserPermission.objects.filter(
            user=user,
            permission_type=permission_type,
            content_type=ContentType.objects.get_for_model(type(obj)),
            object_id=obj.pk,
        ).exists()
