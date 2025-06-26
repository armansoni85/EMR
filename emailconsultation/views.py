import mimetypes  # <-- Add this import at the top

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from .models import ConsultationEmail
from .serializers import ConsultationEmailSerializer
from django.core.mail import EmailMessage
from django.conf import settings

class ConsultationEmailView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def get(self, request):
        emails = ConsultationEmail.objects.all().order_by('-created_at')
        serializer = ConsultationEmailSerializer(emails, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ConsultationEmailSerializer(data=request.data)
        if serializer.is_valid():
            email_data = serializer.save()

            # Send email logic
            email = EmailMessage(
                subject=serializer.validated_data['subject'],
                body=serializer.validated_data['custom_message'],
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[serializer.validated_data['recipient_email']]
            )

            if email_data.document:
                file = email_data.document
                file_name = file.name
                file_content = file.read()

                # Get MIME type using mimetypes
                content_type, _ = mimetypes.guess_type(file_name)
                if content_type is None:
                    content_type = 'application/octet-stream'  # fallback

                email.attach(file_name, file_content, content_type)

            email.send()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
