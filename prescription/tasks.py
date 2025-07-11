from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_refill_reminder(item_id):
    # import the model here, not at module top
    from .models import PrescriptionItem

    try:
        item = (
            PrescriptionItem.objects
            .select_related("prescription__patient", "prescription__doctor")
            .get(id=item_id)
        )
    except PrescriptionItem.DoesNotExist:
        return

    patient = item.prescription.patient
    doctor  = item.prescription.doctor

    subject = f"Refill Reminder for {item.medicine_name}"
    body = (
        f"Hello {patient.get_full_name()},\n\n"
        f"Your supply of {item.medicine_name} is running low. "
        f"You have {item.refills_remaining} refills remaining.\n\n"
        "Please request a refill as soon as possible.\n\n"
        f"— Dr. {doctor.get_full_name()}"
    )

    send_mail(
        subject,
        body,
        settings.DEFAULT_FROM_EMAIL,
        [patient.email, doctor.email],
        fail_silently=False,
    )

