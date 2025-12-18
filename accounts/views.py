from django.contrib.auth import authenticate, login, logout, get_user_model
from django.shortcuts import render, redirect

User = get_user_model()

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('main')
        else:
            return render(request, 'accounts/login.html', {'error': '아이디 또는 비밀번호 오류'})
    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def signup_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        errors = []
        if not username or not password1 or not password2:
            errors.append("모든 값을 입력하세요.")
        if password1 != password2:
            errors.append("비밀번호가 일치하지 않습니다.")
        if User.objects.filter(username=username).exists():
            errors.append("이미 존재하는 아이디입니다.")
        if errors:
            return render(request, 'accounts/signup.html', {'errors': errors})
        User.objects.create_user(username=username, password=password1)
        return redirect('login')
    return render(request, 'accounts/signup.html')