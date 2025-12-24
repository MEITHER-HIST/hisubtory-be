from django.urls import path
from . import views_api

urlpatterns = [
    # 메인 페이지 데이터
    path('v1/main', views_api.main_api_view, name='main_api'),

    # 마이페이지 데이터 (로그인 필요)
    path('v1/mypage', views_api.mypage_api_view, name='mypage_api'),
]

 