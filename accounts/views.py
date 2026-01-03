from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.conf import settings

from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication

from .forms import SignupForm
from library.models import UserViewedEpisode, Bookmark
from .models import Team, TeamMember

User = get_user_model()

# ✅ views_team.py에서도 공통으로 사용할 인증 클래스
class UnsafeSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return 

def get_image_url(ep):
    """이미지 경로를 안전하게 생성하는 공통 헬퍼"""
    try:
        if ep.cuts.exists():
            first_cut = ep.cuts.first()
            if hasattr(first_cut.image, 'url'):
                return first_cut.image.url
            return f"{settings.MEDIA_URL.rstrip('/')}/{str(first_cut.image).lstrip('/')}"
    except: pass
    return "https://via.placeholder.com/150"

# --- [인증 및 기본 뷰] ---
def signup_view(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else: form = SignupForm()
    return render(request, "accounts/signup.html", {"form": form})

@api_view(['POST'])
@authentication_classes([UnsafeSessionAuthentication])
@permission_classes([AllowAny])
def login_view(request):
    data = request.data
    login_id = data.get("username") or data.get("email")
    password = data.get("password")
    
    actual_username = login_id
    if login_id and "@" in login_id:
        try:
            user_obj = User.objects.get(email=login_id)
            actual_username = user_obj.username
        except User.DoesNotExist: pass

    user = authenticate(request, username=actual_username, password=password)
    if user:
        login(request, user)
        return Response({"success": True, "user": {"username": user.username}})
    return Response({"success": False, "message": "로그인 실패"}, status=400)

@api_view(['POST', 'GET'])
@authentication_classes([UnsafeSessionAuthentication])
def logout_view(request):
    logout(request)
    return Response({"success": True}) if request.path.startswith('/api/') else redirect("login")

@api_view(['GET'])
@authentication_classes([UnsafeSessionAuthentication])
@permission_classes([IsAuthenticated])
def me_view(request):
    """현재 로그인한 유저의 기본 상태값 반환"""
    user = request.user
    has_team = Team.objects.filter(leader=user).exists() or TeamMember.objects.filter(user=user).exists()
    return Response({
        "success": True,
        "username": user.username,
        "is_leader_approved": user.is_leader_approved, # 이 값이 True여야 함
        "leader_code": user.leader_code or "",         # 이 값이 전달되어야 함
        "has_team": Team.objects.filter(leader=user).exists() or TeamMember.objects.filter(user=user).exists(),
    })

# --- [개인 활동 로직] ---
@api_view(['GET'])
@authentication_classes([UnsafeSessionAuthentication])
@permission_classes([IsAuthenticated])
def get_user_history(request):
    """내 최근 기록 및 보관함 리스트"""
    user = request.user
    viewed_qs = UserViewedEpisode.objects.filter(user=user).select_related('episode__webtoon__station').order_by('-viewed_at')[:10]
    recent_data = [{"id": r.episode.episode_id, "title": r.episode.subtitle, "stationName": r.episode.webtoon.station.station_name, "imageUrl": get_image_url(r.episode)} for r in viewed_qs]
    
    saved_qs = Bookmark.objects.filter(user=user).select_related('episode__webtoon__station').order_by('-created_at')
    saved_data = [{"id": b.episode.episode_id, "title": b.episode.subtitle, "stationName": b.episode.webtoon.station.station_name, "imageUrl": get_image_url(b.episode)} for b in saved_qs]
    
    return Response({"success": True, "recent": recent_data, "saved": saved_data})