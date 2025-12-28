# accounts/views_api.py
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import ensure_csrf_cookie
from .forms import SignupForm

User = get_user_model()

@ensure_csrf_cookie
def csrf_api_view(request):
    return JsonResponse({"success": True})

@require_POST
def signup_api_view(request):
    form = SignupForm(request.POST)
    if form.is_valid():
        user = form.save()
        return JsonResponse({"success": True, "id": user.id, "username": user.username})
    return JsonResponse({"success": False, "errors": form.errors}, status=400)

@require_POST
def login_api_view(request):
    identifier = request.POST.get("email") or request.POST.get("username")
    password = request.POST.get("password")

    if not identifier or not password:
        return JsonResponse({"success": False, "message": "email/password required"}, status=400)

    # email이면 username으로 바꿔서 authenticate
    if "@" in identifier:
        u = User.objects.filter(email__iexact=identifier).first()
        if not u:
            return JsonResponse({"success": False, "message": "no_user"}, status=400)
        identifier = u.username

    user = authenticate(request, username=identifier, password=password)
    if not user:
        return JsonResponse({"success": False, "message": "invalid_credentials"}, status=400)

    login(request, user)
    return JsonResponse({"success": True, "username": user.username})

@require_POST
@login_required
def logout_api_view(request):
    logout(request)
    return JsonResponse({"success": True})

@login_required
def me_api_view(request):
    user = request.user
    return JsonResponse({"success": True, "id": user.id, "username": user.username, "email": user.email})
