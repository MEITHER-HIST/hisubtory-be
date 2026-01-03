from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

# DRF 관련 임포트
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

from .forms import SignupForm
from library.models import UserViewedEpisode, Bookmark

User = get_user_model()

# ✅ CSRF 검사를 무시하는 세션 인증 클래스 (리액트 연동 필수 설정)
class UnsafeSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return 

# --- [1] 회원가입 및 기본 뷰 ---

def signup_view(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = SignupForm()
    return render(request, "accounts/signup.html", {"form": form})

# --- [2] 로그인 API (JSON/Form 공용) ---

@api_view(['POST'])
@authentication_classes([UnsafeSessionAuthentication])
@permission_classes([AllowAny])
def login_view(request):
    """리액트 JSON 요청과 일반 POST 요청을 모두 처리"""
    data = request.data
    login_id = data.get("username") or data.get("email")
    password = data.get("password")

    if not login_id or not password:
        return Response({"success": False, "message": "아이디와 비밀번호를 입력해주세요."}, status=400)

    # 1. 이메일로 로그인 시도 시 username 찾기
    actual_username = login_id
    if "@" in login_id:
        try:
            user_obj = User.objects.get(email=login_id)
            actual_username = user_obj.username
        except User.DoesNotExist:
            return Response({"success": False, "message": "가입되지 않은 이메일입니다."}, status=400)

    # 2. 인증 및 세션 생성
    user = authenticate(request, username=actual_username, password=password)
    
    if user:
        login(request, user)
        return Response({
            "success": True, 
            "message": "로그인 성공",
            "user": {"username": user.username, "email": user.email}
        })
    else:
        return Response({"success": False, "message": "아이디 또는 비밀번호가 틀렸습니다."}, status=400)

# --- [3] 유저 정보 확인 및 로그아웃 ---

@api_view(['GET'])
@authentication_classes([UnsafeSessionAuthentication])
@permission_classes([IsAuthenticated])
def me_view(request):
    """현재 로그인 상태 확인 및 유저 정보 반환 (401 방지용)"""
    return Response({
        "success": True,
        "username": request.user.username,
        "email": request.user.email,
    })

@api_view(['POST', 'GET'])
@authentication_classes([UnsafeSessionAuthentication])
def logout_view(request):
    logout(request)
    if request.path.startswith('/api/'):
        return Response({"success": True})
    return redirect("login")

# --- [4] 마이페이지 활동 기록 API (library 모델 연동) ---

@api_view(['GET'])
@authentication_classes([UnsafeSessionAuthentication])
@permission_classes([IsAuthenticated])
def get_user_history(request):
    """사용자가 본 에피소드와 북마크한 목록을 반환"""
    user = request.user
    
    # 최근 본 에피소드 (N:1 관계 추적)
    viewed_qs = UserViewedEpisode.objects.filter(user=user).select_related('episode__webtoon__station').order_by('-viewed_at')[:10]
    recent_data = []
    for record in viewed_qs:
        ep = record.episode
        # 컷(Cut) 모델의 첫 이미지를 썸네일로 활용
        img_url = "https://via.placeholder.com/150"
        if ep.cuts.exists():
            first_cut = ep.cuts.first()
            img_url = first_cut.image.url if hasattr(first_cut.image, 'url') else str(first_cut.image)

        recent_data.append({
            "id": ep.episode_id,
            "title": ep.subtitle,
            "stationId": ep.webtoon.station.station_name,
            "imageUrl": img_url,
            "viewed_at": record.viewed_at
        })

    # 저장한 북마크 목록
    saved_qs = Bookmark.objects.filter(user=user).select_related('episode__webtoon__station').order_by('-created_at')
    saved_data = []
    for bookmark in saved_qs:
        ep = bookmark.episode
        img_url = "https://via.placeholder.com/150"
        if ep.cuts.exists():
            first_cut = ep.cuts.first()
            img_url = first_cut.image.url if hasattr(first_cut.image, 'url') else str(first_cut.image)

        saved_data.append({
            "id": ep.episode_id,
            "title": ep.subtitle,
            "stationId": ep.webtoon.station.station_name,
            "imageUrl": img_url,
        })
    
    return Response({
        "success": True,
        "username": user.username,
        "recent": recent_data,
        "saved": saved_data
    })