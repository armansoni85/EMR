from rest_framework import serializers
from .models import ConsultationEmail

class ConsultationEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsultationEmail
        fields = '__all__'
