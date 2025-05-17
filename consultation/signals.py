from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Consultation
from appointments.models import Appointment
from appointments.choices import AppointmentStatus


@receiver(post_save, sender=Consultation)
def update_appointment_status(sender, instance, created, **kwargs):
    """
    Signal receiver that updates the status of an Appointment to 'in_progress'
    when a Consultation instance is saved.

    Args:
        instance (Consultation): The instance of the Consultation model that was saved.
        **kwargs: Additional keyword arguments.

    Returns:
        None
    """
    if created:
        Appointment.objects.filter(id=instance.appointment_id).update(
            appointment_status=AppointmentStatus.in_progress.value[0]
        )
