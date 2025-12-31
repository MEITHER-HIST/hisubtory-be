from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .forms import SignupForm

# API를 위한 임포트 추가
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

User = get_user_model()

# --- 기존 HTML 뷰 (유지) ---

def signup_view(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = SignupForm()
    return render(request, "accounts/signup.html", {"form": form})

def login_view(request):
    error = None
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("main")
        else:
            error = "아이디 또는 비밀번호가 틀렸습니다."
    return render(request, "accounts/login.html", {"error": error})

@login_required
def logout_view(request):
    logout(request)
    return redirect("login")

@login_required
def me_view(request):
    return redirect("main")

# --- 프론트엔드 연동을 위한 API 뷰 (추가) ---
from rest_framework.authentication import SessionAuthentication

# CSRF 검사를 잠시 무시하는 세션 인증 클래스 생성 (개발용)
class UnsafeSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return  # CSRF 체크를 하지 않음

@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication]) # 인증 방식 명시
@permission_classes([IsAuthenticated])  # 로그인된 유저만 접근 가능
def get_user_history(request):
    """프론트엔드 마이페이지에 보낼 활동 기록 API"""
    user = request.user
    
    # [중요] 나중에 RDS(DB) 연동 시 이 부분을 실제 모델 쿼리로 바꾸면 됩니다.
    # 현재는 프론트엔드 화면 확인을 위해 가짜(Mock) 데이터를 보냅니다.
    data = {
        "recent": [
            {
                "id": "1",
                "title": "시작된 여행",
                "stationId": "서울역",
                "imageUrl": "https://via.placeholder.com/150",
                "content": "과거로의 여행이 시작되는 곳입니다."
            },
            {
                "id": "2",
                "title": "독립의 함성",
                "stationId": "서대문역",
                "imageUrl": "https://via.placeholder.com/150",
                "content": "역사의 아픔과 희망이 공존하는 현장입니다."
            }
        ],
        "saved": [] # 저장한 에피소드 데이터
    }
    
    return Response(data)

