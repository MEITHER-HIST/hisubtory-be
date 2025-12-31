from django.urls import path
from . import views

urlpatterns = [
    path('history/', views.get_user_history_api, name='user_history_api'),
]