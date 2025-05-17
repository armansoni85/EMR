from django.urls import path
from .views import AppointmentAPI

urlpatterns = [
    path(
        "", AppointmentAPI.as_view({"get": "list", "post": "post"}), name="appointments"
    ),
    path(
        "<str:pk>/",
        AppointmentAPI.as_view({"get": "get", "put": "put", "delete": "delete"}),
    ),
]
