# accounts/urls_api.py
from django.urls import path
from .views_api import signup_api_view, login_api_view, logout_api_view, me_api_view, csrf_api_view

urlpatterns = [
    path("csrf/", csrf_api_view, name="csrf_api"),
    path("signup/", signup_api_view, name="signup_api"),
    path("login/", login_api_view, name="login_api"),
    path("logout/", logout_api_view, name="logout_api"),
    path("me/", me_api_view, name="me_api"),
]