from __future__ import print_function

import datetime

import firebase_admin
from firebase_admin import messaging
from django.conf import settings
from base.choices import DeviceType
import os


class PushNotification:
    """This class is response for sending push notification"""

    def __init__(
        self,
        service_account_file_path: str = os.path.join(
            settings.BASE_DIR, "firebase_service_account_credentials.json"
        ),
    ) -> None:
        try:
            app = firebase_admin.get_app()
        except ValueError as e:
            cred = firebase_admin.credentials.Certificate(service_account_file_path)
            firebase_admin.initialize_app(cred)

    def android_message(self, registration_fmc_token, title, body):
        """Send push notification on Android"""
        message = messaging.Message(
            android=messaging.AndroidConfig(
                ttl=datetime.timedelta(seconds=3600),
                priority="normal",
                notification=messaging.AndroidNotification(
                    title=title, body=body, icon="stock_ticker_update", color="#f45342"
                ),
            ),
            token=registration_fmc_token,
        )

        return message

    def webpush_message(self, registration_fmc_token, title, body):
        """Send push notification on Web"""
        message = messaging.Message(
            webpush=messaging.WebpushConfig(
                notification=messaging.WebpushNotification(
                    title=title,
                    body=body,
                ),
            ),
            token=registration_fmc_token,
        )

        return message

    def apns_message(self, registration_fmc_token, title, body):
        """Send push notification on IOS"""
        message = messaging.Message(
            apns=messaging.APNSConfig(
                headers={"apns-priority": "10"},
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(
                        alert=messaging.ApsAlert(
                            title=title,
                            body=body,
                        ),
                        badge=42,
                    ),
                ),
            ),
            token=registration_fmc_token,
        )
        return message

    def all_platforms_message(self, registration_fmc_token, title, body):
        """Send push notification on all platform at once"""
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            android=messaging.AndroidConfig(
                ttl=datetime.timedelta(seconds=3600),
                priority="normal",
                notification=messaging.AndroidNotification(
                    icon="stock_ticker_update", color="#f45342"
                ),
            ),
            apns=messaging.APNSConfig(
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(badge=42),
                ),
            ),
            token=registration_fmc_token,
        )

        return message

    def send_push(
        self,
        registration_fmc_token: str = "",
        title: str = "",
        dry_run: bool = False,
        body: str = "",
        device_type: str = "",
    ):
        # raising error if required field is empty coming
        if not all(
            [
                registration_fmc_token,
                title,
                body,
                device_type
                in [
                    DeviceType.android.value[0],
                    DeviceType.web.value[0],
                    DeviceType.ios.value[0],
                ],
            ]
        ):
            raise ValueError(
                "Give all values of mentioned keys: device_type,registration_fmc_token,title,body"
            )

        message = None
        if device_type == DeviceType.android.value[0]:
            message = self.android_message(registration_fmc_token, title, body)

        elif device_type == DeviceType.web.value[0]:
            message = self.webpush_message(registration_fmc_token, title, body)

        elif device_type == DeviceType.ios.value[0]:
            message = self.apns_message(registration_fmc_token, title, body)

        if message:
            if dry_run:
                response = messaging.send(message, dry_run=True)
                return response
            else:
                response = messaging.send(message)
                return response

        return message

    def send_push_in_bulk(
        self, fmc_registration_tokens: list, title: str, body: str, device_type: str
    ):
        # maximum bulk size is 500 => supported by Firebase
        if not all([fmc_registration_tokens, title, body, device_type]):
            raise ValueError(
                "Give all values of mentioned keys: device_type,registration_fmc_token,title,body"
            )

        if len(fmc_registration_tokens) > 500:
            raise ValueError(
                "fmc_registration_tokens size must not exceed more than 500"
            )

        message = None
        if device_type == DeviceType.android.value[0]:
            message = messaging.MulticastMessage(
                android=messaging.AndroidConfig(
                    ttl=datetime.timedelta(seconds=3600),
                    priority="normal",
                    notification=messaging.AndroidNotification(
                        title=title,
                        body=body,
                        icon="stock_ticker_update",
                        color="#f45342",
                    ),
                ),
                tokens=fmc_registration_tokens,
            )

        elif device_type == DeviceType.web.value[0]:
            message = messaging.MulticastMessage(
                webpush=messaging.WebpushConfig(
                    notification=messaging.WebpushNotification(
                        title=title,
                        body=body,
                    ),
                ),
                tokens=fmc_registration_tokens,
            )

        elif device_type == DeviceType.ios.value[0]:
            message = messaging.MulticastMessage(
                apns=messaging.APNSConfig(
                    headers={"apns-priority": "10"},
                    payload=messaging.APNSPayload(
                        aps=messaging.Aps(
                            alert=messaging.ApsAlert(
                                title=title,
                                body=body,
                            ),
                            badge=42,
                        ),
                    ),
                ),
                tokens=fmc_registration_tokens,
            )

        response = messaging.send_multicast(message)
        if response.failure_count > 0:
            responses = response.responses
            failed_tokens = []
            for idx, resp in enumerate(responses):
                if not resp.success:
                    # The order of responses corresponds to the order of the registration tokens.
                    failed_tokens.append(fmc_registration_tokens[idx])

            return failed_tokens

        return response
