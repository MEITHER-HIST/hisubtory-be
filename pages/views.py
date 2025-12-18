from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from transit.models import Station
from stories.models import Episode
from activity.models import UserViewedEpisode
import random

def main_view(request):
    # 1. 오픈된 노선 가져오기 (3호선만 활성화)
    lines = Station.objects.filter(is_enabled=True).values_list('line', flat=True).distinct()
    
    # 선택 노선 (default: 3호선)
    line = request.GET.get('line', '3호선')

    # 2. 선택 노선의 역 목록
    stations = Station.objects.filter(line=line, is_enabled=True)

    # 3. 랜덤 역 선택
    random_station = random.choice(list(stations)) if stations else None
    random_episode = None
    if random_station:
        episodes = Episode.objects.filter(station=random_station)
        if episodes:
            random_episode = random.choice(list(episodes))

    # 4. 로그인 유저 정보
    user = request.user if request.user.is_authenticated else None
    viewed_episodes = []
    if user:
        viewed_episodes = user.viewed_episodes.values_list('episode_id', flat=True)

    context = {
        'lines': lines,
        'line': line,
        'stations': stations,
        'random_station': random_station,
        'random_episode': random_episode,
        'viewed_episodes': viewed_episodes,
        'user': user,
    }
    return render(request, 'pages/main.html', context)

@login_required
def mypage_view(request):
    user = request.user
    # 최근 본 10개의 에피소드
    recent_episodes = UserViewedEpisode.objects.filter(user=user).order_by('-viewed_at')[:10]
    context = {
        'user': user,
        'recent_episodes': recent_episodes,
    }
    return render(request, 'pages/mypage.html', context)