import csv
import logging
import os
import secrets
from io import StringIO
import io
import requests
import json
import boto3
import firebase_admin
import requests
from celery.signals import task_failure, task_success, task_prerun
from django.conf import settings
from django.db.models import Prefetch, F
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from firebase_admin import credentials, messaging

from emr.celery import common_app as app


from django.core.mail import send_mail, EmailMessage, EmailMultiAlternatives

from django.utils.html import strip_tags
from django.template.loader import render_to_string
from django.db import transaction
import magic
from base.push_notification import PushNotification
from notification.models import NotificationSent
from base.choices import DeviceType


# cred = credentials.Certificate(os.path.join(settings.BASE_DIR, 'google-service-account.json'))
# firebase_admin.initialize_app(cred)

logger = logging.getLogger("__name__")


@app.task()
def send_mail_task(subject, html_message, recipient_list):
    from_email = f"{settings.EMAIL_FROM_NAME} <{settings.DEFAULT_FROM_EMAIL}>"

    send_mail(
        subject=subject,
        message=strip_tags(html_message),
        html_message=html_message,
        from_email=from_email,
        recipient_list=recipient_list,
    )
    return {"Recipients": recipient_list, "Subject": subject}


@app.task()
def send_email_with_attachment(
    subject, message, from_email, recipient_list, attachment_path
):
    """Can be used in future where there is required to send email with attachment"""
    with open(attachment_path, "rb") as file:
        file_content = file.read()

    mime_type = magic.from_buffer(file_content, mime=True)

    # Extract the filename from the attachment_path
    file_name = os.path.basename(attachment_path)

    email = EmailMessage(subject, message, from_email, recipient_list)
    email.attach(file_name, file_content, mime_type)

    # Send the email
    email.send()


@task_failure.connect()
def celery_task_failure_email(**kwargs):
    subject = "Celery Error: Task {sender.name} ({task_id}): {exception} | Project: {project_name}".format(
        **kwargs, project_name=settings.EMAIL_FROM_NAME
    )
    message = """Task {sender.name} with id {task_id} raised exception:
        {exception!r}
        Task was called with args: {args} kwargs: {kwargs}.
        The contents of the full traceback was:
        {einfo}
    """.format(
        **kwargs
    )

    admin_emails = list(map(lambda x: x[1], settings.ADMINS))
    if admin_emails:
        send_mail_task(subject, message, admin_emails)


@task_success.connect()
def celery_task_success(sender, **kwargs):
    """
    This function will be called when a task succeeds.
    """
    task_id = sender.request.id
    task_result = kwargs["result"]


@task_prerun.connect()
def celery_task_prerun(sender=None, task_id=None, task=None, **kwargs):
    """
    This function will be called just before a task starts executing.
    """

    task_name_parts = sender.name.split(".")  # Split task name by dot
    task_name = task_name_parts[-1]  # Take the last part after the dot


@app.task()
def send_push_notifications(
    fmc_registration_token_with_device_type_list: list = [],
    notification_type: str = "",
    title: str = "",
    body: str = "",
    is_mobile: bool = False,
    is_web: bool = False,
    user_id: str = "",
):
    """
    fmc_registration_token_with_device_type_list=[{"token":"32323ffdffsf","device_type":"WEB"}]
    Eg:Calling this function
    # if fmc_registration_tokens_list:
    #     send_push_notifications(
    #         fmc_registration_token_with_device_type_list= json.dumps(fmc_registration_tokens_list),
    #         is_mobile= user.is_mobile_push_notification_enable,
    #         is_web=user.is_web_push_notification_enable,
    #         user_id=str(user.id),
    #         notification_type=NotificationType.login.value[0],
    #         title="Authentication",
    #         body="Logged in successfully from 127.0.0.1:8000",
    #     )

    send_push_notifications.apply_async(
        kwargs={
            "fmc_registration_token_with_device_type_list": json.dumps(fmc_registration_tokens_list),
            "is_mobile": user.is_mobile_push_notification_enable,
            "is_web":user.is_web_push_notification_enable,
            "user_id":str(user.id),
            "notification_type":NotificationType.login.value[0],
            "title":"Authentication",
            "body":"Logged in successfully from 127.0.0.1:8000",

        }
    )
    """
    fmc_registration_token_with_device_type_list = json.loads(
        fmc_registration_token_with_device_type_list
    )
    if not fmc_registration_token_with_device_type_list or not any([is_web, is_mobile]):
        return

    notification_instances_to_create = []
    is_push_notification_sent = True
    push_notification = PushNotification()  # initializing push notification

    for fmc_registration_dict in fmc_registration_token_with_device_type_list:
        device_type = fmc_registration_dict.get("device_type")
        token = fmc_registration_dict.get("token")

        # if invalid device_type then continue else proceed ahead
        if device_type not in [
            DeviceType.ios.value[0],
            DeviceType.android.value[0],
            DeviceType.web.value[0],
        ]:
            continue

        elif device_type and token:
            try:
                if is_mobile:
                    push_notification.send_push(
                        registration_fmc_token=token,
                        title=title,
                        body=body,
                        device_type=device_type,
                    )
                    is_push_notification_sent = True

                if is_web:
                    push_notification.send_push(
                        registration_fmc_token=token,
                        title=title,
                        body=body,
                        device_type=device_type,
                    )
                    is_push_notification_sent = True

            except Exception as e:
                # unable to send push notification
                is_push_notification_sent = False

            finally:
                notification_instances_to_create.append(
                    NotificationSent(
                        user_id=user_id,
                        fmc_registration_token=token,
                        is_sent=is_push_notification_sent,
                        notification_type=notification_type,
                        title=title,
                        body=body,
                        device_type=device_type,
                    )
                )

    if notification_instances_to_create:
        # store notification in Notification
        NotificationSent.objects.bulk_create(
            notification_instances_to_create,
            batch_size=settings.BATCH_SIZE_USER_DATA_PREPARE,
        )

    return {"message": "Notification Sent"}


def create_push_notification_instances_with_success_failed(
    all_registration_tokens: list,
    failed_registration_tokens: list,
    user_id: str,
    title: str,
    body: str,
    notification_type: str,
    device_type: str,
) -> list:
    if not isinstance(
        failed_registration_tokens, list
    ):  # if failed then then we will failed_token in list otherwise we will get firebase_obj
        return [
            NotificationSent(
                user_id=user_id,
                fmc_registration_token=registration_fmc_token,
                is_sent=True,
                notification_type=notification_type,
                title=title,
                body=body,
                device_type=device_type,
            )
            for registration_fmc_token in all_registration_tokens
        ]

    notification_instances = []
    for registration_fmc_token in all_registration_tokens:
        push_notification_instance = NotificationSent(
            user_id=user_id,
            fmc_registration_token=registration_fmc_token,
            is_sent=True,
            notification_type=notification_type,
            title=title,
            body=body,
            device_type=device_type,
        )
        if registration_fmc_token in failed_registration_tokens:
            setattr(push_notification_instance, "is_sent", False)

        notification_instances.append(push_notification_instance)

    return notification_instances


@app.task()
def send_bulk_push_notifications_in_batch(
    fmc_registration_token_with_device_type_list: str,
    notification_type: str = "",
    title: str = "",
    body: str = "",
    is_mobile: bool = False,
    is_web: bool = False,
    user_id: str = "",
):
    """sending push_notfication in batch .Note maximum push_notification size  in batch process is 500"""
    fmc_registration_token_with_device_type_list = json.loads(
        fmc_registration_token_with_device_type_list
    )

    if not fmc_registration_token_with_device_type_list or all(
        [not is_web, not is_mobile]
    ):
        return
    notification_instances_to_create = []
    push_notification = PushNotification()  # initializing push notification
    # categorizing push token based on device_type
    web_push_fmc_registration_token = []
    android_push_fmc_registration_token = []
    ios_push_fmc_registration_token = []
    for fmc_registration_dict in fmc_registration_token_with_device_type_list:
        device_type = fmc_registration_dict.get("device_type")
        token = fmc_registration_dict.get("token")

        # if invalid device_type then continue else proceed ahead
        if device_type not in [
            DeviceType.ios.value[0],
            DeviceType.android.value[0],
            DeviceType.web.value[0],
        ]:
            continue

        elif device_type and token:
            if device_type == DeviceType.web.value[0] and is_web:
                web_push_fmc_registration_token.append(token)

            elif device_type == DeviceType.android.value[0] and is_mobile:
                android_push_fmc_registration_token.append(token)

            elif device_type == DeviceType.android.value[0] and is_mobile:
                ios_push_fmc_registration_token.append(token)

    if web_push_fmc_registration_token:
        failed_push_notification_token_list = push_notification.send_push_in_bulk(
            fmc_registration_tokens=web_push_fmc_registration_token,
            title=title,
            body=body,
            device_type=DeviceType.web.value[0],
        )
        push_notification_instances = (
            create_push_notification_instances_with_success_failed(
                all_registration_tokens=web_push_fmc_registration_token,
                failed_registration_tokens=failed_push_notification_token_list,
                user_id=user_id,
                title=title,
                body=body,
                notification_type=notification_type,
                device_type=DeviceType.web.value[0],
            )
        )
        notification_instances_to_create.extend(push_notification_instances)

    if android_push_fmc_registration_token:
        failed_push_notification_token_list = push_notification.send_push_in_bulk(
            android_push_fmc_registration_token,
            device_type=DeviceType.android.value[0],
            title=title,
            body=body,
        )
        push_notification_instances = (
            create_push_notification_instances_with_success_failed(
                all_registration_tokens=android_push_fmc_registration_token,
                failed_registration_tokens=failed_push_notification_token_list,
                user_id=user_id,
                title=title,
                body=body,
                notification_type=notification_type,
                device_type=DeviceType.android.value[0],
            )
        )
        notification_instances_to_create.extend(push_notification_instances)

    if ios_push_fmc_registration_token:
        failed_push_notification_token_list = push_notification.send_push_in_bulk(
            ios_push_fmc_registration_token,
            device_type=DeviceType.ios.value[0],
            title=title,
            body=body,
        )
        push_notification_instances = (
            create_push_notification_instances_with_success_failed(
                all_registration_tokens=ios_push_fmc_registration_token,
                failed_registration_tokens=failed_push_notification_token_list,
                user_id=user_id,
                title=title,
                body=body,
                notification_type=notification_type,
                device_type=DeviceType.ios.value[0],
                is_web=True,
            )
        )
        notification_instances_to_create.extend(push_notification_instances)

    if notification_instances_to_create:
        # store notification in Notification
        NotificationSent.objects.bulk_create(
            notification_instances_to_create,
            batch_size=settings.BATCH_SIZE_USER_DATA_PREPARE,
        )

    return {"message": "Notification sent in bulk"}


# def test_bulk():
#     fmc_registration_token_with_device_type_list=[{"token":"fP2xlibJ50cvZQwDnwgtMW:APA91bENVabnxGuSM6QbkKC54ZJirhnTIGgcuSAy-61FVE-0DtJ3MHuqR2defTKY02W6qiTsTOwDnDcr-oQ2mBb2cIOS72mzASmvJYujtdD7IhZjeMZfiwW3o5P6XOuxKZgbDY4h7yFw","device_type":DeviceType.web.value[0]}]
#     from notification.choices import NotificationType
#     fmc_registration_token_with_device_type_list=json.dumps(fmc_registration_token_with_device_type_list)
#     user_id='bd0e98e1-7885-4a8f-a695-3343dfbb0473'
#     send_bulk_push_notifications_in_batch(fmc_registration_token_with_device_type_list=fmc_registration_token_with_device_type_list,notification_type=NotificationType.login.value[0],title='Authentication',body='Logged In',user_id=user_id,is_web=True)
