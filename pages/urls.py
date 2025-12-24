from django.urls import path
from . import views

urlpatterns = [
    # 템플릿 뷰
    path('', views.main_view, name='main'),
    path('mypage/', views.mypage_view, name='mypage'),
] 
