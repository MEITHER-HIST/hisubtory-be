from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .forms import SignupForm

User = get_user_model()

def signup_view(request):
    """회원가입 HTML 페이지 렌더링"""
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = SignupForm()

    return render(request, "accounts/signup.html", {"form": form})


def login_view(request):
    """로그인 HTML 페이지 렌더링"""
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
    """로그아웃 HTML 처리"""
    logout(request)
    return redirect("login")


@login_required
def me_view(request):
    """HTML에서는 내 정보 페이지 대신 메인으로 이동"""
    return redirect("main")

