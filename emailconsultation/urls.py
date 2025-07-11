from django.urls import path
from .views import ConsultationEmailView

urlpatterns = [
    path('consultation-emails/', ConsultationEmailView.as_view(), name='consultation-email'),
]
