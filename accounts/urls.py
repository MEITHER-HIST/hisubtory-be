# accounts/urls.py
from django.urls import path
from . import views, views_team

urlpatterns = [
    # views.py: 인증 및 개인 기본 정보
    path('login/', views.login_view),
    path('logout/', views.logout_view),
    path('me/', views.me_view),
    path('history/', views.get_user_history),

    # views_team.py: 팀 관련 모든 기능 (주소 일치 확인!)
    path('team-info/', views_team.get_team_shared_bookmarks),
    path('membership-request/', views_team.membership_request_view), # 함수 위치 변경
    path('team/action/<int:request_id>/', views_team.handle_team_request),
]