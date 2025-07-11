# views.py

from datetime import datetime, timedelta
from django.utils.timezone import now
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from appointments.models import Appointment
from appointments.serializers import AppointmentSerializer
from user.models import CustomUser
from user.serializers import CustomUserSerializer


class AppointmentsByDateAPIView(APIView):
    def get(self, request):
        date_str = request.query_params.get("date")  # format: YYYY-MM-DD

        if not date_str:
            return Response(
                {"error": "Date parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"error": "Invalid date format. Use YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        appointments = Appointment.objects.filter(
            appointment_datetime__date=selected_date, doctor=self.request.user
        ).select_related("doctor", "patient")

        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PatientStatsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        doctor = request.user  # logged-in doctor
        today = now().date()
        start_of_this_month = today.replace(day=1)
        start_of_last_month = (start_of_this_month - timedelta(days=1)).replace(day=1)
        end_of_last_month = start_of_this_month - timedelta(days=1)

        # Total patients created by this doctor
        total_patients = CustomUser.objects.filter(created_by=doctor, role="3").count()

        # Last month’s patient count
        last_month_patients = CustomUser.objects.filter(
            created_by=doctor,
            role="patient",
            date_joined__date__gte=start_of_last_month,
            date_joined__date__lte=end_of_last_month,
        ).count()

        # This month's new patients
        this_month_patients = CustomUser.objects.filter(
            created_by=doctor,
            role="patient",
            date_joined__date__gte=start_of_this_month,
        ).count()

        difference = total_patients - last_month_patients
        change = difference if difference != 0 else 0
        increase = change > 0

        return Response(
            {
                "total_patients": total_patients,
                "last_month_patients": last_month_patients,
                "this_month_patients": this_month_patients,
                "difference_from_last_month": abs(change),
                "is_increase": increase,
            }
        )


class CurrentMonthPatientsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        doctor = request.user
        today = now().date()
        start_of_month = today.replace(day=1)
        yesterday = today - timedelta(days=1)

        # All patients created this month
        current_month_patients = CustomUser.objects.filter(
            created_by=doctor, role="3", date_joined__date__gte=start_of_month
        )

        # Count till yesterday
        till_yesterday_count = current_month_patients.filter(
            date_joined__date__lte=yesterday
        ).count()

        # Count today
        today_count = current_month_patients.filter(date_joined__date=today).count()

        change = today_count
        is_increase = change > 0

        # Serialize patient list (optional, for response)
        serialized_patients = CustomUserSerializer(
            current_month_patients, many=True
        ).data

        return Response(
            {
                "total_current_month_patients": current_month_patients.count(),
                "patients": serialized_patients,
                "patients_till_yesterday": till_yesterday_count,
                "patients_today": today_count,
                "difference_from_yesterday": abs(change),
                "is_increase": is_increase,
            }
        )

