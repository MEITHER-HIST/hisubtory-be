from django.shortcuts import render, redirect
from subway.models import Station, Line
from stories.models import Episode
from library.models import UserViewedEpisode
from accounts.models import User
import random
from django.contrib.auth.decorators import login_required


def main_view(request):
    # 1️⃣ 노선 목록
    lines = Line.objects.all()

    # 2️⃣ 선택된 노선 (default: 3호선)
    line_num = request.GET.get('line', '3')
    try:
        line_int = int(line_num)
    except ValueError:
        line_int = 3

    line_obj = Line.objects.filter(line_name=f"{line_int}호선").first()

    # 3️⃣ 해당 노선의 역들
    stations = Station.objects.none()
    if line_obj:
        stations = Station.objects.filter(stationline__line=line_obj).distinct()

    # 4️⃣ 로그인 유저
    user = request.user if request.user.is_authenticated else None

    # 5️⃣ 유저가 본 역 ID 목록
    viewed_station_ids = set()
    if user:
        viewed_station_ids = set(
            UserViewedEpisode.objects.filter(user=user)
            .values_list('episode__station_id', flat=True)
        )

    # 6️⃣ 랜덤 버튼 클릭 시 바로 랜덤 스토리 페이지로 이동
    if request.GET.get('random') == '1' and stations.exists():
        if user:
            # 로그인 O: 안 본 역 후보
            candidate_stations = [s for s in stations if s.id not in viewed_station_ids]

            # 모든 역 봤거나 후보 없으면, 안 본 에피 있는 역 후보
            if not candidate_stations:
                candidate_stations = [s for s in stations if Episode.objects.filter(station=s).exclude(
                    id__in=UserViewedEpisode.objects.filter(user=user).values_list('episode_id', flat=True)
                ).exists()]

            # 그래도 후보 없으면 모든 역에서 랜덤
            if not candidate_stations:
                candidate_stations = list(stations)
        else:
            # 로그인 X: 전체 역에서 랜덤
            candidate_stations = list(stations)

        random_station = random.choice(candidate_stations)

        episodes = Episode.objects.filter(station=random_station)
        if user:
            episodes = episodes.exclude(
                id__in=UserViewedEpisode.objects.filter(user=user).values_list('episode_id', flat=True)
            )

        if episodes.exists():
            random_episode = random.choice(list(episodes))
            if user:
                UserViewedEpisode.objects.get_or_create(user=user, episode=random_episode)
            # 랜덤 에피가 선택되면 바로 상세 페이지로 이동
            return redirect('episode_detail', episode_id=random_episode.id)
        else:
            # 에피가 하나도 없으면 랜덤 역 페이지 표시(선택적으로 처리 가능)
            pass

    # 7️⃣ 역 상태 계산
    station_list = []
    for s in stations:
        station_data = {
            'id': s.id,
            'name': s.station_name,
            'latitude': s.latitude,
            'longitude': s.longitude,
            'clickable': bool(user),
            'color': 'green' if user and s.id in viewed_station_ids else 'gray'
        }
        station_list.append(station_data)

    # 8️⃣ 템플릿 전달
    context = {
        'lines': lines,
        'selected_line': line_obj,
        'stations': station_list,
        'user': user,
    }

    return render(request, 'pages/main.html', context)


@login_required
def mypage_view(request):
    user = request.user

    recent_views = UserViewedEpisode.objects.filter(
        user=user
    ).select_related(
        'episode'
    ).order_by('-viewed_at')[:10]

    viewed_station_ids = set(
        recent_views.values_list('episode__station_id', flat=True)
    )

    viewed_stations = Station.objects.filter(id__in=viewed_station_ids)
    all_stations = Station.objects.all()  # 마커 테스트용

    context = {
        'user': user,
        'recent_views': recent_views,
        'viewed_stations': viewed_stations,
        'viewed_station_ids': viewed_station_ids,
        'all_stations': all_stations,
    }
    return render(request, 'pages/mypage.html', context)
