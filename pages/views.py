from django.shortcuts import render, redirect
from subway.models import Station, Line
from stories.models import Episode
from library.models import UserViewedEpisode, Bookmark
from django.contrib.auth.decorators import login_required
from django.db.models import IntegerField, Case, When
from django.db.models.functions import Cast, Substr
import random

# ===========================
# 헬퍼 함수: 에피소드 선택 로직
# ===========================
def get_episode(user, station_id, fetch_unseen=True):
    # ✅ 수정: station_id 대신 webtoon__station_id 사용 (명세 반영)
    episodes = Episode.objects.filter(webtoon__station_id=station_id)

    if user and user.is_authenticated and fetch_unseen:
        # ✅ 수정: PK 필드명 pk -> episode_id (또는 기본 pk 유지 가능하나 명세상 episode_id)
        seen_ids = UserViewedEpisode.objects.filter(user=user).values_list("episode_id", flat=True)
        episodes = episodes.exclude(episode_id__in=seen_ids)

    # 안 본 게 없으면 전체에서 다시 선택
    if not episodes.exists():
        episodes = Episode.objects.filter(webtoon__station_id=station_id)

    if episodes.exists():
        ep = random.choice(list(episodes))
        if user and user.is_authenticated:
            UserViewedEpisode.objects.get_or_create(user=user, episode=ep)
        return ep
    return None


# ===========================
# 메인 화면 뷰
# ===========================
def main_view(request):
    # 1️⃣ 노선 목록 가져오기 + 정렬
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
        display_name = line.line_name + ('' if is_active else ' (준비중)')
        line_list.append({
            'id': line.id,
            'line_name': display_name,
            'is_active': is_active
        })

    # 2️⃣ 선택된 노선 처리
    line_num = request.GET.get('line', '3')
    try:
        line_int = int(line_num)
    except ValueError:
        line_int = 3
    line_obj = Line.objects.filter(line_name=f"{line_int}호선").first()

    # 3️⃣ 역 목록 (팀장님 명세 8번 기준 is_enabled 필터링)
    stations = Station.objects.filter(is_enabled=True) if line_obj else Station.objects.none()

    # 4️⃣ 로그인 유저 및 시청 기록
    user = request.user if request.user.is_authenticated else None
    viewed_station_ids = set()
    if user:
        # ✅ 수정: 관계 경로 episode__webtoon__station_id (명세 2-3번 계층 반영)
        viewed_station_ids = set(
            UserViewedEpisode.objects.filter(user=user)
            .values_list("episode__webtoon__station_id", flat=True)
        )

    # 5️⃣ 역 클릭 처리
    clicked_station_id = request.GET.get('clicked_station')
    if clicked_station_id:
        try:
            clicked_station_id = int(clicked_station_id)
            episode_id_for_redirect = None

            if user:
                # ✅ 수정: episode__webtoon__station_id 사용
                viewed_episodes = UserViewedEpisode.objects.filter(
                    user=user,
                    episode__webtoon__station_id=clicked_station_id
                )
                if viewed_episodes.exists():
                    last_episode = viewed_episodes.latest('viewed_at').episode
                    episode_id_for_redirect = last_episode.episode_id # id -> episode_id
                else:
                    ep = get_episode(user, clicked_station_id)
                    if ep:
                        episode_id_for_redirect = ep.episode_id
            else:
                ep = get_episode(user, clicked_station_id)
                if ep:
                    episode_id_for_redirect = ep.episode_id

            if episode_id_for_redirect:
                return redirect('episode_detail', episode_id=episode_id_for_redirect)
        except ValueError:
            pass

    # 6️⃣ 랜덤 스토리 버튼 처리
    if request.GET.get('random') == '1' and stations.exists():
        candidate_stations = list(stations)
        if user:
            candidate_stations = [s for s in stations if s.id not in viewed_station_ids]
            if not candidate_stations:
                candidate_stations = list(stations)

        random_station = random.choice(candidate_stations)
        ep = get_episode(user, random_station.id)
        if ep:
            return redirect('episode_detail', episode_id=ep.episode_id)

    # 7️⃣ 역 상태 표시
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
        'show_random_button': stations.exists(),
    }
    return render(request, 'pages/main.html', context)


# ===========================
# 마이페이지 뷰
# ===========================
@login_required
def mypage_view(request):
    user = request.user

    # 1️⃣ 최근 본 에피소드 (✅ 수정: episode__webtoon__station 관계 추적)
    recent_views = UserViewedEpisode.objects.filter(
        user=user
    ).select_related(
        'episode', 'episode__webtoon__station'
    ).order_by('-viewed_at')[:10]

    # 2️⃣ 북마크한 에피소드
    bookmarked_episodes = Bookmark.objects.filter(
        user=user
    ).select_related(
        'episode', 'episode__webtoon__station'
    ).order_by('-created_at')

    # ✅ 수정: station_id 추출 시 경로 수정
    viewed_station_ids = set(
        recent_views.values_list('episode__webtoon__station_id', flat=True)
    )
    viewed_stations = Station.objects.filter(id__in=viewed_station_ids)

    context = {
        'user': user,
        'recent_views': recent_views,
        'bookmarked_episodes': bookmarked_episodes,
        'recent_count': recent_views.count(),
        'bookmark_count': bookmarked_episodes.count(),
        'viewed_stations': viewed_stations,
        'viewed_station_ids': viewed_station_ids,
    }
    return render(request, 'pages/mypage.html', context)