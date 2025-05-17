from django.urls import path
from hospital import views


urlpatterns = [
    path("", views.HospitalAPI.as_view({"get": "list", "post": "post"})),
    path(
        "<str:pk>/",
        views.HospitalAPI.as_view({"get": "get", "put": "put", "delete": "delete"}),
    ),
]
