from django.urls import path
from .views import AppointmentsByDateAPIView, PatientStatsAPIView, CurrentMonthPatientsAPIView

# urlpatterns = [
#     path('', AppointmentsByDateAPIView.as_view({'get': 'list'}), name='appointments-by-date'),
# ]

urlpatterns = [
path('', AppointmentsByDateAPIView.as_view(), name='appointments-by-date'),
path('patient-status', PatientStatsAPIView.as_view(), name='patient-stats'),
path('doctor/monthly-patients/', CurrentMonthPatientsAPIView.as_view()),
]
