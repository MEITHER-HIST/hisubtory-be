from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .forms import SignupForm
import re

User = get_user_model()

# 아이디 검증
def validate_username(username):
    if not username:
        return "아이디를 입력하세요."
    if len(username) < 4 or len(username) > 20:
        return "아이디는 4~20자여야 합니다."
    if not re.match(r'^[a-zA-Z0-9]+$', username):
        return "아이디는 영어와 숫자만 사용할 수 있습니다."
    return None

# 비밀번호 검증
def validate_password(password):
    if len(password) < 6:
        return "비밀번호는 6자 이상이어야 합니다."
    return None

def signup_view(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = SignupForm()

    return render(request, "accounts/signup.html", {
        "form": form
    })


def login_view(request):
    error = None

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user:
            login(request, user)
            return redirect("main")
        else:
            error = "아이디 또는 비밀번호가 틀렸습니다."

    return render(request, "accounts/login.html", {
        "error": error
    })


# 로그아웃
def logout_view(request):
    logout(request)
    if request.headers.get("Accept") == "application/json":
        return JsonResponse({"message": "로그아웃 완료"})
    return redirect('login')  # 웹 브라우저는 로그인 페이지로 이동


# 내 정보 확인
@login_required
def me_view(request):
    user = request.user
    if request.headers.get("Accept") == "application/json":
        return JsonResponse({"username": user.username})
    return redirect('main')  # 웹 브라우저는 페이지 이동만


@require_POST
def login_common(request):
    email = request.POST.get("email")
    password = request.POST.get("password")

    user = authenticate(request, email=email, password=password)

    if not user:
        if is_api(request):
            return JsonResponse({
                "success": False,
                "message": "로그인 실패"
            }, status=400)

        return render(request, "accounts/login.html", {
            "error": "이메일 또는 비밀번호가 틀렸습니다."
        })

    login(request, user)

    if is_api(request):
        return JsonResponse({
            "success": True
        })

    return redirect("main")