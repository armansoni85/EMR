from django.db import models

class ConsultationEmail(models.Model):
    recipient_email = models.EmailField()
    recipient_name = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    document = models.FileField(upload_to='consultation_documents/')
    custom_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subject} to {self.recipient_email}"

