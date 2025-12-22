from django.urls import path
from . import views

urlpatterns = [
    # 마이페이지 데이터 가져오기 (accounts 앱에서 관리할 수도 있지만, library 기록 기반일 경우 여기 둠)
    path('mypage/', views.my_page_api, name='my_page_api'),
    
    # 이야기 저장하기 (이미 구현한 save_story_api 연결)
    path('save/<int:episode_id>/', views.save_story_api, name='save_story_api'),
]