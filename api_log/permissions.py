from rest_framework.permissions import BasePermission
from strings import *
from user.choices import MQGADMINUSERS, COMPANY_USERS, MERCHANT_USERS, RoleType


class CanReadAuditLogs(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if any(
                [
                    x in MQGADMINUSERS + COMPANY_USERS + MERCHANT_USERS
                    for x in request.user.roles
                ]
            ):
                return True
            return False
        return False


class CanReadMQGLogs(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if any(
                [
                    x in MQGADMINUSERS + COMPANY_USERS + MERCHANT_USERS
                    for x in request.user.roles
                ]
            ):
                return True
            return False
        return False


class CanDownloadMQGLogs(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if any(
                [
                    x
                    in [
                        RoleType.mqg_admin.value[0],
                        RoleType.mqg_supervisor.value[0],
                        RoleType.company_admin.value[0],
                        RoleType.company_supervisor.value[0],
                        RoleType.merchant_admin.value[0],
                    ]
                    for x in request.user.roles
                ]
            ):
                return True
            return False
        return False


class CanDownloadATIONETAPILogs(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if any([x in MQGADMINUSERS for x in request.user.roles]):
                return True
            return False
        return False
