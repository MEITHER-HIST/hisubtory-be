# accounts/urls.py
from django.urls import path
from . import views, views_team

urlpatterns = [
    # 회원가입 경로 추가
    path('signup/', views.signup_view, name='signup'), 
    
    # 기존 경로들
    path('login/', views.login_view),
    path('logout/', views.logout_view),
    path('me/', views.me_view),
    path('history/', views.get_user_history),
    path('membership-request/', views_team.membership_request_view),
    path('team-info/', views_team.get_team_shared_bookmarks),
    path('team/action/<int:request_id>/', views_team.handle_team_request),
]