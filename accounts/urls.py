from rest_framework_simplejwt.views import TokenRefreshView
from django.urls import path
from . import views

urlpatterns = [
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/login/", views.LoginView.as_view()),
    path("auth/register/", views.RegisterAPIView.as_view()),
    path("request-reset/", views.RequestPasswordReset.as_view()),
    path("reset-password/<uidb64>/<token>/", views.ResetPassword.as_view()),
]
