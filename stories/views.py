from django.shortcuts import get_object_or_404, redirect, render
from .models import Episode
from subway.models import Station
from library.models import UserViewedEpisode
import random

# --- 1. 역 클릭 시 해당 역 랜덤 에피소드 선택 후 main 페이지로 redirect ---
def station_stories(request, station_id):
    station = get_object_or_404(Station, id=station_id)
    episodes = Episode.objects.filter(station=station)
    if not episodes.exists():
        return redirect('/')

    # 랜덤 에피 선택
    episode = random.choice(list(episodes))

    # 로그인 유저면 클릭만으로 본 기록 저장
    if request.user.is_authenticated:
        UserViewedEpisode.objects.get_or_create(user=request.user, episode=episode)

    # main_view로 line 파라미터 붙여서 redirect
    line_name = station.stationline.first().line.line_name  # 예: "3호선"
    return redirect(f'/?line={line_name[:-2]}')

# --- 2. 에피소드 상세 페이지 ---
def episode_detail_view(request, episode_id):
    episode = get_object_or_404(Episode, id=episode_id)

    # 로그인 유저면 본 기록 저장
    if request.user.is_authenticated:
        UserViewedEpisode.objects.get_or_create(user=request.user, episode=episode)

    return render(request, 'stories/detail.html', {'episode': episode})

# --- 3. 전체 역 랜덤 스토리 버튼 ---
def random_episode_view(request):
    stations = Station.objects.filter(is_enabled=True)
    if not stations.exists():
        return redirect('/')

    if request.user.is_authenticated:
        viewed_station_ids = UserViewedEpisode.objects.filter(
            user=request.user
        ).values_list('episode__station_id', flat=True)

        candidate_stations = [s for s in stations if s.id not in viewed_station_ids]
        if not candidate_stations:
            candidate_stations = list(stations)
    else:
        candidate_stations = list(stations)

    random_station = random.choice(candidate_stations)
    episodes = Episode.objects.filter(station=random_station)

    if request.user.is_authenticated:
        episodes = episodes.exclude(
            id__in=UserViewedEpisode.objects.filter(user=request.user).values_list('episode_id', flat=True)
        )

    if not episodes.exists():
        return redirect('/')

    random_episode = random.choice(list(episodes))
    if request.user.is_authenticated:
        UserViewedEpisode.objects.get_or_create(user=request.user, episode=random_episode)

    # main_view로 line 파라미터 붙여서 redirect
    line_name = random_station.stationline.first().line.line_name
    return redirect(f'/?line={line_name[:-2]}')
