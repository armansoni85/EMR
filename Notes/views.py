from django.shortcuts import render
from rest_framework import generics
from .models import Note
from .serializers import NoteSerializer

# Create and List all notes
class NoteListCreateView(generics.ListCreateAPIView):
    queryset = Note.objects.all().order_by('-date_time')
    serializer_class = NoteSerializer

    def get_queryset(self):
        return Note.objects.filter(doctor=self.request.user).order_by('-date_time')

    def perform_create(self, serializer):
        serializer.save(doctor=self.request.user)

# Retrieve, Update, and Delete specific note
class NoteDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer

