from django.urls import path
from . import views

urlpatterns = [
    # Main 화면 데이터 (역 목록 등)
    path('v1/main/', views.main_view, name='main_api'),
    
]