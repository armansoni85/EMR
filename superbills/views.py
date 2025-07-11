from django.shortcuts import render
from rest_framework import viewsets, filters
from .models import ICDCode, CPTCode
from .serializers import ICDCodeSerializer, CPTCodeSerializer

class ICDCodeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    list/retrieve ICD Codes. 
    Supports search by code or description via ?search=…
    """
    queryset = ICDCode.objects.all()
    serializer_class = ICDCodeSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["code", "description"]


class CPTCodeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    list/retrieve CPT Codes.
    Supports search by code or description via ?search=…
    """
    queryset = CPTCode.objects.all()
    serializer_class = CPTCodeSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["code", "description"]

