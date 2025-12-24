from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .forms import SignupForm


@require_POST
def signup_api_view(request):
    form = SignupForm(request.POST)
    if form.is_valid():
        form.save()
        return JsonResponse({"success": True})
    return JsonResponse(
        {"success": False, "errors": form.errors},
        status=400
    )


@require_POST
def login_api_view(request):
    username = request.POST.get("username")
    password = request.POST.get("password")

    user = authenticate(request, username=username, password=password)
    if not user:
        return JsonResponse(
            {"success": False, "message": "로그인 실패"},
            status=400
        )

    login(request, user)
    return JsonResponse({
        "success": True,
        "username": user.username
    })


@require_POST
@login_required
def logout_api_view(request):
    logout(request)
    return JsonResponse({"success": True})


@login_required
def me_api_view(request):
    user = request.user
    return JsonResponse({
        "success": True,
        "id": user.id,
        "username": user.username
    })  
