from django.urls import path
from .views import main_view, mypage_view

urlpatterns = [
    path('', main_view, name='main'),
    path('mypage/', mypage_view, name='mypage'),
]