from base.choices import ChoiceEnum


class AppointmentStatus(ChoiceEnum):
    """
    Enumeration of appointment statuses:
    - PENDING: Appointment is awaiting confirmation or action.
    - IN_PROGRESS: Appointment is currently being handled.
    - REJECTED: Appointment was declined or skipped.
    - DONE: Appointment has been completed successfully.
    """

    pending = ("PENDING", "Pending")
    in_progress = ("IN_PROGRESS", "In Progress")
    rejected = ("REJECTED", "Rejected")
    done = ("DONE", "Done")
