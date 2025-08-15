from django.urls import path
from document import views


urlpatterns = [
    path("", views.MedicalDocumentAPI.as_view({"get": "list", "post": "post"})),
    path(
        "<str:pk>/",
        views.MedicalDocumentAPI.as_view(
            {"get": "get", "put": "put", "delete": "delete"}
        ),
    ),
]
