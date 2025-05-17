from base.tasks import app
from notification.models import NotificationSent
from django.utils.timezone import datetime, timedelta
from django.utils import timezone
from django.conf import settings


@app.task()
def delete_notifications_older_three_months(
    days: int = settings.NOTIFICATION_TO_BE_DELETED_AFTER_X_DAYS,
):
    """
    This will clear notification sent which are older than three months
    """

    NotificationSent.objects.filter(
        created_at__lt=datetime.now(tz=timezone.utc) - timedelta(days=days)
    ).delete()

    return {"message": f"Notifications older than {days} days deleted ."}
