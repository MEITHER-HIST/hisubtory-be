from django.urls import path
<<<<<<< HEAD
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('signup/', views.signup_view, name='signup'),
    
    # [화면] 주소창에 /api/accounts/mypage/ 입력 시 작동
    path('mypage/', views.mypage_screen, name='mypage'),
    
    # [데이터] JS가 내부적으로 데이터를 호출하는 주소
    path('api/mypage/', views.my_page_api, name='mypage_api'),
=======
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup_view, name='signup'),
    path('me/', views.me_view, name='me'),
>>>>>>> 0d6b3f83263c69e43d272063447f5061c2759c13
]