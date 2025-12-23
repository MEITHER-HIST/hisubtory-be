from django.shortcuts import render, redirect
from subway.models import Station, Line
from stories.models import Episode
from library.models import UserViewedEpisode
from django.contrib.auth.decorators import login_required
from django.db.models import IntegerField, Case, When
from django.db.models.functions import Cast, Substr
import random

from django.shortcuts import render, redirect
from subway.models import Station, Line
from stories.models import Episode
from library.models import UserViewedEpisode
from django.contrib.auth.decorators import login_required
from django.db.models import IntegerField, Case, When
from django.db.models.functions import Cast, Substr
import random

def main_view(request):
    # 1️⃣ 노선 목록 (1~9호선 숫자 순, 3호선 맨 위)
    lines = Line.objects.annotate(
        line_number=Cast(Substr('line_name', 1, 1), IntegerField()),
        priority=Case(
            When(line_name='3호선', then=0),  # 3호선 우선
            default=1,
            output_field=IntegerField()
        )
    ).order_by('priority', 'line_number')

    # 1-1️⃣ 3호선을 제외한 나머지 이름 뒤에 (준비중) 추가
    line_list = []
    for line in lines:
        display_name = line.line_name
        if line.line_name != '3호선':
            display_name += ' (준비중)'
        line_list.append({
            'id': line.id,
            'line_name': display_name,
            'is_active': line.line_name == '3호선'
        })

    # 2️⃣ 선택된 노선 (default: 3호선)
    line_num = request.GET.get('line', '3')
    try:
        line_int = int(line_num)
    except ValueError:
        line_int = 3
    line_obj = Line.objects.filter(line_name=f"{line_int}호선").first()

    # 3️⃣ 해당 노선의 활성 역 목록
    stations = Station.objects.none()
    if line_obj:
        stations = Station.objects.filter(
            stationline__line=line_obj,
            is_enabled=True
        ).distinct()

    # 랜덤 버튼 표시 여부: 활성화된 역이 하나라도 있으면 True
    show_random_button = stations.exists()

    # 4️⃣ 로그인 유저 확인
    user = request.user if request.user.is_authenticated else None

    # 5️⃣ 로그인 유저가 본 역 ID 목록
    viewed_station_ids = set()
    if user:
        viewed_station_ids = set(
            UserViewedEpisode.objects.filter(user=user)
            .values_list('episode__station_id', flat=True)
        )

    # 6️⃣ 에피소드 선택 함수
    def get_episode(station_id, fetch_unseen=True):
        episodes = Episode.objects.filter(station_id=station_id)
        if user and fetch_unseen:
            episodes = episodes.exclude(
                id__in=UserViewedEpisode.objects.filter(user=user).values_list('episode_id', flat=True)
            )
        if not episodes.exists() and fetch_unseen:
            episodes = Episode.objects.filter(station_id=station_id)
        if episodes.exists():
            ep = random.choice(list(episodes))
            if user:
                UserViewedEpisode.objects.get_or_create(user=user, episode=ep)
            return ep
        return None

    # 7️⃣ 클릭한 역 처리
    clicked_station_id = request.GET.get('clicked_station')
    if clicked_station_id:
        try:
            clicked_station_id = int(clicked_station_id)
            episode_id_for_redirect = None
            if user:
                # 로그인 O
                viewed_episodes = UserViewedEpisode.objects.filter(user=user, episode__station_id=clicked_station_id)
                if viewed_episodes.exists():
                    # 초록색 역: 마지막 본 에피
                    last_episode = viewed_episodes.latest('viewed_at').episode
                    episode_id_for_redirect = last_episode.id
                else:
                    # 회색 역: 새로운 에피
                    ep = get_episode(clicked_station_id)
                    if ep:
                        episode_id_for_redirect = ep.id
            else:
                # 비회원: 첫 에피
                ep = get_episode(clicked_station_id)
                if ep:
                    episode_id_for_redirect = ep.id

            if episode_id_for_redirect:
                return redirect('episode_detail', episode_id=episode_id_for_redirect)

        except ValueError:
            pass

    # 8️⃣ 랜덤 스토리 버튼 처리
    if request.GET.get('random') == '1' and stations.exists():
        candidate_stations = list(stations)
        if user:
            candidate_stations = [s for s in stations if s.id not in viewed_station_ids]
            if not candidate_stations:
                candidate_stations = list(stations)
        random_station = random.choice(candidate_stations)
        ep = get_episode(random_station.id)
        if ep:
            return redirect('episode_detail', episode_id=ep.id)

    # 9️⃣ 역 상태 계산 (마커 색상)
    station_list = []
    for s in stations:
        station_list.append({
            'id': s.id,
            'name': s.station_name,
            'clickable': bool(user),
            'color': 'green' if user and s.id in viewed_station_ids else 'gray'
        })

    # 10️⃣ 템플릿 전달
    context = {
        'lines': line_list,  # 수정된 라인 리스트 전달
        'selected_line': line_obj,
        'stations': station_list,
        'user': user,
        'show_random_button': show_random_button,  # 랜덤 버튼 변수 추가
    }
    return render(request, 'pages/main.html', context)


@login_required
def mypage_view(request):
    user = request.user
    recent_views = UserViewedEpisode.objects.filter(
        user=user
    ).select_related('episode').order_by('-viewed_at')[:10]

    viewed_station_ids = set(
        recent_views.values_list('episode__station_id', flat=True)
    )
    viewed_stations = Station.objects.filter(id__in=viewed_station_ids)

    context = {
        'user': user,
        'recent_views': recent_views,
        'viewed_stations': viewed_stations,
        'viewed_station_ids': viewed_station_ids,
    }
    return render(request, 'pages/mypage.html', context)
