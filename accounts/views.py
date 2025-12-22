from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json

# [기능 1] 가입
def signup_view(request):
    from .forms import SignUpForm
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            from django.contrib.auth import login
            login(request, user)
            return redirect('main')
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})

# [기능 2] 마이페이지 화면 보여주기
@login_required
def mypage_screen(request):
    return render(request, 'accounts/mypage.html')

# [기능 3] 마이페이지 데이터 보내주기
@login_required
def my_page_api(request):
    try:
        from library.models import UserActivity
        user = request.user
        recent = UserActivity.objects.filter(user=user).order_by('-last_viewed_at')[:5]
        saved = UserActivity.objects.filter(user=user, is_saved=True)
        
        recent_data = [{"station": s.episode.station.name, "last_viewed": s.last_viewed_at.strftime("%Y-%m-%d %H:%M")} for s in recent]
        saved_data = [{"station": s.episode.station.name, "image": s.episode.images.first().image.url if s.episode.images.exists() else None} for s in saved]
        
        return JsonResponse({"recent_stories": recent_data, "saved_stories": saved_data}, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)