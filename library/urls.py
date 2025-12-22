# library/urls.py
from django.urls import path
from . import views

app_name = 'library'  # 앱 이름 공간 설정

urlpatterns = [
    # 1. 이야기 저장하기: /api/library/save/5/ 형식으로 호출
    path('save/<int:episode_id>/', views.save_story_api, name='save_story'),
    
    # 2. 마이페이지 데이터: /api/library/mypage/ 형식으로 호출
    path('mypage/', views.my_page_api, name='my_page'),
]