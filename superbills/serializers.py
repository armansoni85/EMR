from rest_framework import serializers
from .models import ICDCode, CPTCode

class ICDCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ICDCode
        fields = ("code", "description")


class CPTCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CPTCode
        fields = ("code", "description")

