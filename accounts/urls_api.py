from django.urls import path
from .views import login_common

urlpatterns = [
    path("login/", login_common),
]