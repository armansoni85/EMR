from django.urls import path
from user import views


urlpatterns = [
    path("login/", views.LoginView.as_view({"post": "create"})),
    path("profile/", views.ProfileAPI.as_view({"get": "retrieve"})),
    path("password/", views.PasswordChangeAPI.as_view()),
    path(
        "verify-password-token/new-password/",
        views.PasswordTokenVerifyWithNewPassAPI.as_view(),
    ),
    path("verify-password-token/", views.PasswordTokenVerifyAPI.as_view()),
    path("refresh-token/", views.RefreshTokenView.as_view({"post": "create"})),
    path("logout/", views.LogoutView.as_view({"post": "create"})),
    path("", views.UserViewsetAPI.as_view({"get": "list", "post": "post"})),
    path(
        "<str:pk>/",
        views.UserViewsetAPI.as_view({"get": "get", "put": "put", "delete": "delete"}),
    ),
]
