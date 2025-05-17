from django.urls import path
from employee import views


urlpatterns = [
    path(
        "professional-info/",
        views.ProfessionalInformationAPI.as_view({"get": "list", "post": "post"}),
    ),
    path(
        "professional-info/<str:pk>/",
        views.ProfessionalInformationAPI.as_view({"get": "get", "put": "put"}),
    ),
    path("duty-detail/", views.DutyDetailAPI.as_view({"get": "list", "post": "post"})),
    path(
        "duty-detail/<str:pk>/",
        views.DutyDetailAPI.as_view({"get": "get", "put": "put"}),
    ),
    path(
        "qualification/",
        views.QualificationAPI.as_view({"get": "list", "post": "post"}),
    ),
    path(
        "qualification/<str:pk>/",
        views.QualificationAPI.as_view({"get": "get", "put": "put"}),
    ),
    path(
        "certification/",
        views.CertificationsAPI.as_view({"get": "list", "post": "post"}),
    ),
    path(
        "certification/<str:pk>/",
        views.CertificationsAPI.as_view({"get": "get", "put": "put"}),
    ),
]
