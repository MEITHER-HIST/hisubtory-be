from django.shortcuts import render, redirect, get_object_or_404
from subway.models import Station, Line
from stories.models import Episode
from library.models import UserViewedEpisode
from django.contrib.auth.decorators import login_required
from django.db.models import IntegerField, Case, When
from django.db.models.functions import Cast, Substr
import random
from django.utils import timezone

# ===========================
# 메인 화면 뷰
# ===========================
def main_view(request):
    lines = Line.objects.annotate(
        line_number=Cast(Substr('line_name', 1, 1), IntegerField()),
        is_active_calc=Case(
            When(line_name='3호선', then=1),
            default=0,
            output_field=IntegerField()
        )
    ).order_by('-is_active_calc', 'line_number')

    line_list = []
    for line in lines:
        is_active = bool(line.is_active_calc)
        display_name = line.line_name
        if not is_active:
            display_name += ' (준비중)'
        line_list.append({
            'id': line.id,
            'line_name': display_name,
            'is_active': is_active
        })

    line_num = request.GET.get('line', '3')
    try:
        line_int = int(line_num)
    except ValueError:
        line_int = 3
    line_obj = Line.objects.filter(line_name=f"{line_int}호선").first()

    stations = Station.objects.none()
    if line_obj:
        stations = Station.objects.filter(
            stationline__line=line_obj,
            is_enabled=True
        ).distinct()

    show_random_button = stations.exists()
    user = request.user if request.user.is_authenticated else None

    viewed_station_ids = set()
    if user:
        viewed_station_ids = set(
            UserViewedEpisode.objects.filter(user=user)
            .values_list('episode__webtoon__station_id', flat=True)
        )

    # 안전하게 Episode 가져오기
    def get_episode(station_id, fetch_unseen=True):
        episodes = Episode.objects.filter(webtoon__station_id=station_id).select_related('webtoon', 'webtoon__station')
        if user and fetch_unseen:
            episodes = episodes.exclude(
                id__in=UserViewedEpisode.objects.filter(user=user)
                .values_list('episode_id', flat=True)
            )
        if not episodes.exists() and fetch_unseen:
            episodes = Episode.objects.filter(webtoon__station_id=station_id).select_related('webtoon', 'webtoon__station')
        if episodes.exists():
            ep = random.choice(list(episodes))
            if user and ep.webtoon and ep.webtoon.station:
                # FK 안전하게 넣어서 생성
                UserViewedEpisode.objects.get_or_create(
                    user=user,
                    episode=ep,
                    station=ep.webtoon.station
                )
            return ep
        return None

    # 역 클릭 처리
    clicked_station_id = request.GET.get('clicked_station')
    if clicked_station_id:
        try:
            clicked_station_id = int(clicked_station_id)
            episode_id_for_redirect = None
            if user:
                viewed_episodes = UserViewedEpisode.objects.filter(
                    user=user,
                    episode__webtoon__station_id=clicked_station_id
                )
                if viewed_episodes.exists():
                    last_episode = viewed_episodes.latest('viewed_at').episode
                    episode_id_for_redirect = last_episode.id
                else:
                    ep = get_episode(clicked_station_id)
                    if ep:
                        episode_id_for_redirect = ep.id
            else:
                ep = get_episode(clicked_station_id)
                if ep:
                    episode_id_for_redirect = ep.id
            if episode_id_for_redirect:
                return redirect('episode_detail', episode_id=episode_id_for_redirect)
        except ValueError:
            pass

    # 랜덤 버튼 처리
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

    # 역 상태 표시
    station_list = []
    for s in stations:
        station_list.append({
            'id': s.id,
            'name': s.station_name,
            'clickable': bool(user),
            'color': 'green' if user and s.id in viewed_station_ids else 'gray'
        })

    context = {
        'lines': line_list,
        'selected_line': line_obj,
        'stations': station_list,
        'user': user,
        'show_random_button': show_random_button,
    }
    return render(request, 'pages/main.html', context)


# ===========================
# 마이페이지 뷰
# ===========================
@login_required
def mypage_view(request):
    user = request.user

    recent_views = UserViewedEpisode.objects.filter(user=user)\
        .select_related('episode', 'episode__webtoon', 'episode__webtoon__station')\
        .order_by('-viewed_at')[:10]

    saved_episodes = UserViewedEpisode.objects.filter(user=user, saved=True)\
        .select_related('episode', 'episode__webtoon', 'episode__webtoon__station')\
        .order_by('-saved_at')

    recent_count = recent_views.count()
    saved_count = saved_episodes.count()

    viewed_station_ids = set(recent_views.values_list('episode__webtoon__station_id', flat=True))
    viewed_stations = Station.objects.filter(id__in=viewed_station_ids)

    context = {
        'user': user,
        'recent_views': recent_views,
        'saved_episodes': saved_episodes,
        'recent_count': recent_count,
        'saved_count': saved_count,
        'viewed_stations': viewed_stations,
        'viewed_station_ids': viewed_station_ids,
    }
    return render(request, 'pages/mypage.html', context)


# ===========================
# 에피소드 저장 / 토글
# ===========================
@login_required
def toggle_save_episode(request, episode_id):
    user = request.user
    episode = get_object_or_404(Episode, id=episode_id)
    if episode.webtoon and episode.webtoon.station:
        obj, created = UserViewedEpisode.objects.get_or_create(
            user=user,
            episode=episode,
            station=episode.webtoon.station
        )
        if obj.saved:
            obj.saved = False
            obj.saved_at = None
        else:
            obj.saved = True
            obj.saved_at = timezone.now()
        obj.save()
    return redirect('episode_detail', episode_id=episode_id)
