from django.urls import path
from consultation import views


urlpatterns = [
    path(
        "recordings/",
        views.ConsultationRecordingAPI.as_view({"get": "list", "post": "post"}),
    ),
    path(
        "recordings/analyze/<str:consultation_id>/",
        views.ConsultationRecordingAnalyze.as_view(),
    ),
    path(
        "recordings/<str:pk>/",
        views.ConsultationRecordingAPI.as_view({"get": "get"}),
    ),
    path("", views.ConsultationAPI.as_view({"get": "list", "post": "post"})),
    path(
        "<str:pk>/",
        views.ConsultationAPI.as_view({"get": "get", "put": "put"}),
    ),
]
