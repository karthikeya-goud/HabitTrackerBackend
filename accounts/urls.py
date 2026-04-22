from rest_framework_simplejwt.views import TokenRefreshView
from django.urls import path
from . import views

urlpatterns = [
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/login/", views.LoginView.as_view()),
    path("auth/register/", views.RegisterAPIView.as_view()),
]
