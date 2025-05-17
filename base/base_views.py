from django.core import exceptions
from django.utils import timezone
from typing import Union
from collections import OrderedDict

from base.utils import success_response
from rest_framework import serializers
from rest_framework import (
    status as status_code,
)  # since there are places which gets conflict because of same name
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import (
    ListModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    CreateModelMixin,
    RetrieveModelMixin,
)

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_tracking_logger.mixins import LoggingMixin
from emr.handle_exceptions import (
    handler_exception_general,
    handler_exception_404,
    get_response_data_errors,
)
from strings import *
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.exceptions import APIException
from django.utils.translation import gettext as _
from django.db import transaction


class CustomListModelMixin(ListModelMixin):
    @transaction.atomic
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = self.get_paginated_response(serializer.data).data
        else:
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data

        return success_response(data=data)


from base.utils import LoginThrottleRate


class CustomViewSetV2(viewsets.GenericViewSet, CustomListModelMixin):
    model_class = None
    one_serializer_class = None
    list_serializer_class = None
    create_serializer_class = None
    update_serializer_class = None
    response_serializer_class = None
    serializer = None
    resp = []
    field_pk = "pk"
    lookup_field = "pk"

    def initial(self, request, *args, **kwargs):
        """
        Runs anything that needs to occur prior to calling the method handler.
        """
        self.format_kwarg = self.get_format_suffix(**kwargs)

        # Perform content negotiation and store the accepted info on the request
        neg = self.perform_content_negotiation(request)
        request.accepted_renderer, request.accepted_media_type = neg

        # Determine the API version, if versioning is in use.
        version, scheme = self.determine_version(request, *args, **kwargs)
        request.version, request.versioning_scheme = version, scheme

        # Ensure that the incoming request is permitted
        self.check_throttles(request)
        self.perform_authentication(request)
        self.check_permissions(request)

    def handle_exception(self, exc):
        if isinstance(exc, KeyError):
            exc = serializers.ValidationError(
                detail={exc.args[0]: ["This field is required"]}
            )
        return super().handle_exception(exc)

    def get_response(
        self, message: str = "", data: Union[dict, list] = {}, status: int = 200
    ):
        request = self.request
        if len(self.resp) > 0:
            message = self.resp[0]
            data = self.resp[1]
            status = self.resp[2]
        response_data = dict()

        success = (
            True
            if status == status_code.HTTP_200_OK
            or status == status_code.HTTP_201_CREATED
            else False
        )
        message = data.pop("message") if "message" in data else message
        detail = data.pop("detail") if "detail" in data else None
        code = data.pop("code") if "code" in data else ""
        response_data["success"] = success

        if request and request.session:
            if "code" in request.session:
                code = request.session["code"]
                del request.session["code"]

        if not success:
            if status == status_code.HTTP_404_NOT_FOUND and len(code) == 0:
                code = "not_found"
            if status == status_code.HTTP_422_UNPROCESSABLE_ENTITY and len(code) == 0:
                code = "unprocessable_entity"
            if len(code) == 0:
                code = "bad_request"

        if success:
            if isinstance(data, list):
                response_data["data"] = data
            elif isinstance(data, dict) and len(data):
                response_data["data"] = data
        if len(code) > 0:
            response_data["code"] = code

        if code == "no_permissions":
            status = status_code.HTTP_403_FORBIDDEN
        if isinstance(message, str):
            response_data["message"] = (
                message.strip() if message else ("ok" if success else "error")
            )
        else:
            response_data["message"] = message

        response_data["detail"] = detail
        return Response(response_data, status=status)

    # def get_queryset_filters(self, queryset_class, *args, **kwargs):
    #     return {}

    # def get_queryset_excludes(self, *args, **kwargs):
    #     return {}

    # def get_queryset(self, *args, **kwargs):
    #     filters = self.get_queryset_filters(*args, **kwargs)
    #     if len(filters) > 0:
    #         return self.model_class.objects.filter(**filters)
    #     else:
    #         return self.model_class.objects.all()

    # def list(self, request, *args, **kwargs):
    #     try:
    #         # queryset = self.get_queryset()
    #         serializer = self.get_list_serializer(queryset, many=True)
    #         self.make_response_success(data=serializer.data)
    #     except Exception as e:
    #         self.resp = handler_exception_general(__name__, e)
    #     finally:
    #         return self.get_response()

    def get_select_related_one(self):
        return []

    def get_prefetch_related_one(self):
        return []

    # def get_object(self, pk=None, filters: dict = {}, values: list = []):
    #     if pk:
    #         filters = {self.lookup_field: pk}
    #     if len(values) == 0:
    #         return self.model_class.objects.select_related(
    #             *self.get_select_related_one()
    #         ).prefetch_related(
    #             *self.get_prefetch_related_one()
    #         ).get(**filters)
    #     else:
    #         return self.model_class.objects.values(*values).get(**filters)
    @transaction.atomic
    def retrieve(self, request, *args, **kwargs):
        try:
            pk = kwargs.pop(self.field_pk)
            simple = request.query_params.get("simple", "false")
            register = self.get_queryset().get(pk=pk)

            if simple == "false":
                self.serializer = self.get_one_serializer(register)
            else:
                self.serializer = self.get_serializer(register)
            self.make_response_success(data=self.serializer.data)
        except self.model_class.DoesNotExist:
            self.make_response_not_found()
        except exceptions.ValidationError as e:
            self.resp = handler_exception_404(__name__, self.lookup_field, pk, e)
        except Exception as e:
            self.resp = handler_exception_general(__name__, e)
        finally:
            return self.get_response()

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        request_data = (
            request.data if "request_data" not in kwargs else kwargs["request_data"]
        )

        self.serializer = self.get_create_serializer(data=request_data)
        if self.serializer.is_valid():
            self.perform_create(request, *args, **kwargs)
        else:
            self.resp = get_response_data_errors(self.serializer.errors, version="v2")

        return self.get_response()

    @transaction.atomic
    def perform_create(self, request, *args, **kwargs):
        response_simple = False if "simple" not in kwargs else kwargs["simple"]
        register = self.serializer.save()
        if response_simple:
            response_data = {"status": "ok"}
        else:
            if not self.response_serializer_class:
                response_data = self.serializer.data
            else:
                response_data = self.response_serializer_class(register).data
        self.make_response_success(
            data=response_data, status=status_code.HTTP_201_CREATED
        )

    def make_response_success(
        self, message: str = "", data: Union[dict, list] = None, status: int = 200
    ):
        self.resp = [message, data, status]

    def make_response_not_found(self):
        self.resp = ["Record not found", {}, status_code.HTTP_404_NOT_FOUND]

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        try:
            request_data = (
                request.data if "request_data" not in kwargs else kwargs["request_data"]
            )
            pk = kwargs.pop(self.field_pk)

            register = self.get_queryset().get(pk=pk)

            self.serializer = self.get_update_serializer(
                register, data=request_data, partial=True
            )
            if self.serializer.is_valid():
                self.perform_update(request, *args, **kwargs)
            else:
                self.resp = get_response_data_errors(
                    self.serializer.errors, version="v2"
                )
        except exceptions.ValidationError as e:
            self.resp = handler_exception_404(__name__, self.lookup_field, pk, e)
        except self.model_class.DoesNotExist:
            self.make_response_not_found()
        except Exception as e:
            self.resp = handler_exception_general(__name__, e)
        finally:
            return self.get_response()

    @transaction.atomic
    def perform_update(self, request, *args, **kwargs):
        response_simple = False if "simple" not in kwargs else kwargs["simple"]
        register = self.serializer.save()
        if response_simple:
            response_data = {"status": "ok"}
        else:
            if not self.response_serializer_class:
                response_data = self.serializer.data
            else:
                response_data = self.response_serializer_class(register).data
        self.make_response_success(data=response_data)

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        try:
            pk = kwargs.pop(self.field_pk)
            self.perform_destroy(
                request, register=self.get_queryset().get(pk=pk), *args, **kwargs
            )
        except self.model_class.DoesNotExist:
            self.make_response_not_found()
        except exceptions.ValidationError as e:
            self.resp = handler_exception_404(__name__, self.lookup_field, pk, e)
        except Exception as e:
            self.resp = handler_exception_general(__name__, e)
        finally:
            return self.get_response()

    @transaction.atomic
    def perform_destroy(self, request, *args, **kwargs):
        register = kwargs["register"]
        # if hasattr(register, 'status'):
        #     register.status = Status.objects.get(slug='deleted')
        #     if hasattr(register, 'deleted_at'):
        #         register.deleted_at = timezone.now()
        #     register.save()
        register.delete()
        self.make_response_success(
            "Registro borrado", {}, status_code.HTTP_204_NO_CONTENT
        )

    def get_list_serializer(self, *args, **kwargs):
        serializer_class = self.get_list_serializer_class()
        kwargs["context"] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    def get_list_serializer_class(self):
        if self.list_serializer_class:
            return self.list_serializer_class
        else:
            return self.get_serializer_class()

    def get_one_serializer(self, *args, **kwargs):
        serializer_class = self.get_one_serializer_class()
        kwargs["context"] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    def get_one_serializer_class(self):
        if self.one_serializer_class:
            return self.one_serializer_class
        else:
            return self.get_serializer_class()

    def get_create_serializer(self, *args, **kwargs):
        serializer_class = self.get_create_serializer_class()
        kwargs["context"] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    def get_create_serializer_class(self):
        if self.create_serializer_class:
            return self.create_serializer_class
        else:
            return self.get_serializer_class()

    def get_update_serializer(self, *args, **kwargs):
        serializer_class = self.get_update_serializer_class()
        kwargs["context"] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    def get_update_serializer_class(self):
        if self.update_serializer_class:
            return self.update_serializer_class
        else:
            return self.get_serializer_class()

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs["context"] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    def get_serializer_class(self):
        assert self.serializer_class is not None, (
            "'%s' should either include a `serializer_class` attribute, "
            "or override the `get_serializer_class()` method." % self.__class__.__name__
        )

        return self.serializer_class

    def get_serializer_context(self):
        return {"request": self.request, "format": self.format_kwarg, "view": self}


class CustomAPIView(LoggingMixin, APIView):
    def handle_exception(self, exc):
        if isinstance(exc, KeyError):
            exc = serializers.ValidationError(
                detail={exc.args[0]: ["This field is required"]}
            )
        return super().handle_exception(exc)


class CustomLimitOffsetPagination(LimitOffsetPagination):
    max_limit = 100


class CustomViewSetWithPaginationV2(CustomViewSetV2):
    pagination_class = CustomLimitOffsetPagination

    @property
    def paginator(self):
        """
        The paginator instance associated with the view, or `None`.
        """
        if not hasattr(self, "_paginator"):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = self.pagination_class()
        return self._paginator

    def paginate_queryset(self, queryset):
        """
        Return a single page of results, or `None` if pagination is disabled.
        """
        if self.paginator is None:
            return None
        return self.paginator.paginate_queryset(queryset, self.request, view=self)

    def get_paginated_response(self, data):
        """
        Return a paginated style `Response` object for the given output data.
        """
        assert self.paginator is not None

        pages = int(self.paginator.count / self.paginator.limit)
        current_page = self.paginator.offset / self.paginator.limit

        return OrderedDict(
            [
                ("pages", pages),
                ("current_page", current_page),
                ("limit", self.paginator.limit),
                ("offset", self.paginator.offset),
                ("count", self.paginator.count),
                ("next", self.paginator.get_next_link()),
                ("previous", self.paginator.get_previous_link()),
                ("results", data),
            ]
        )

    def get_response_from_export(self, export):
        return export

    def list(self, request, *args, **kwargs):
        response = None
        try:
            self.queryset = self.get_queryset(*args, **kwargs)
            export = request.query_params.get("export", None)
            if not export:
                page = self.paginate_queryset(self.queryset)
                if page is not None:
                    serializer = self.get_list_serializer(page, many=True)
                    response_data = self.get_paginated_response(serializer.data)
                    self.make_response_success(data=response_data)
            elif export:
                response = self.get_response_from_export(export=export)
        except Exception as e:
            self.resp = handler_exception_general(__name__, e)
        finally:
            if not response:
                return self.get_response()
            return response
