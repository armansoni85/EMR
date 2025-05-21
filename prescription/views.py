from django.shortcuts import render

from rest_framework import viewsets, permissions
from .models import Prescription
from .serializers import PrescriptionSerializer

class PrescriptionViewSet(viewsets.ModelViewSet):
    """
    list/create/update/delete prescriptions.
    """
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # if doctor, show only their prescriptions
        if user.role and "doctor" in user.role:
            return self.queryset.filter(doctor=user)
        # if patient, show only theirs
        if user.role and "patient" in user.role:
            return self.queryset.filter(patient=user)
        # admin / superuser sees all
        return self.queryset

