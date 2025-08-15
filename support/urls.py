from django.urls import path
from support import views


urlpatterns = [
    path(
        "ai-chat/",
        views.AIChatSupportView.as_view({"get": "list", "post": "post"}),
    ),
    path(
        "ai-chat/<str:pk>/",
        views.AIChatSupportView.as_view({"get": "get"}),
    ),
]
