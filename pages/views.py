# pages/views.py
from django.shortcuts import render, redirect
from subway.models import Station, Line
from stories.models import Episode
from library.models import UserViewedEpisode, Bookmark
from django.contrib.auth.decorators import login_required
from django.db.models import IntegerField, Case, When
from django.db.models.functions import Cast, Substr
from django.http import JsonResponse
import random


# ===========================
# 메인 화면 뷰
# ===========================
def main_view(request):
    # 1️⃣ 노선 목록 가져오기 + 정렬
    # - line_number: '1호선' 같은 이름에서 첫 글자를 숫자로 변환
    # - is_active_calc: 현재 활성화된 노선만 표시 (3호선)
    lines = Line.objects.annotate(
        line_number=Cast(Substr('line_name', 1, 1), IntegerField()),
        is_active_calc=Case(
            When(line_name='3호선', then=1),
            default=0,
            output_field=IntegerField()
        )
    ).order_by(
        '-is_active_calc',  # 활성 노선 먼저
        'line_number'       # 숫자 순
    )

    # 1-1️⃣ 노선 표시용 리스트 구성
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

    # 2️⃣ 선택된 노선 처리 (GET 파라미터 ?line=3, 기본 3호선)
    line_num = request.GET.get('line', '3')
    try:
        line_int = int(line_num)
    except ValueError:
        line_int = 3
    line_obj = Line.objects.filter(line_name=f"{line_int}호선").first()

    # 3️⃣ 선택된 노선의 활성 역 목록 가져오기
    stations = Station.objects.none()
    if line_obj:
        stations = Station.objects.filter(
            is_enabled=True
        ).distinct()

    # 4️⃣ 랜덤 스토리 버튼 표시 여부
    show_random_button = stations.exists()

    # 5️⃣ 로그인 유저 확인
    user = request.user if request.user.is_authenticated else None

    # 6️⃣ 유저가 본 역 ID 가져오기
    viewed_station_ids = set(
        UserViewedEpisode.objects.filter(user=user)
        .values_list("episode__webtoon__station_id", flat=True)
    )

    # 7️⃣ 에피소드 선택 함수 정의
    # pages/views.py

def get_episode(station_id, fetch_unseen=True):
    episodes = Episode.objects.filter(webtoon__station_id=station_id)

    if user and fetch_unseen:
        seen_ids = UserViewedEpisode.objects.filter(user=user).values_list("episode_id", flat=True)
        episodes = episodes.exclude(pk__in=seen_ids)

    if not episodes.exists() and fetch_unseen:
        episodes = Episode.objects.filter(webtoon__station_id=station_id)

    if episodes.exists():
        ep = random.choice(list(episodes))
        if user:
            UserViewedEpisode.objects.get_or_create(user=user, episode=ep)
        return ep
    return None


    # 8️⃣ 역 클릭 처리 (GET 파라미터 ?clicked_station=ID)
    clicked_station_id = request.GET.get('clicked_station')
    if clicked_station_id:
        try:
            clicked_station_id = int(clicked_station_id)
            episode_id_for_redirect = None

            if user:
                # 유저가 이미 본 에피가 있다면 마지막 에피로
                viewed_episodes = UserViewedEpisode.objects.filter(
                    user=user,
                    episode__station_id=clicked_station_id
                )
                if viewed_episodes.exists():
                    last_episode = viewed_episodes.latest('viewed_at').episode
                    episode_id_for_redirect = last_episode.id
                else:
                    ep = get_episode(clicked_station_id)
                    if ep:
                        episode_id_for_redirect = ep.id
            else:
                # 비로그인 유저는 랜덤 선택
                ep = get_episode(clicked_station_id)
                if ep:
                    episode_id_for_redirect = ep.id

            # 에피소드가 있으면 episode_detail로 리다이렉트
            if episode_id_for_redirect:
                return redirect('episode_detail', episode_id=episode_id_for_redirect)

        except ValueError:
            pass  # clicked_station이 숫자가 아니면 무시

    # 9️⃣ 랜덤 스토리 버튼 처리 (GET ?random=1)
    if request.GET.get('random') == '1' and stations.exists():
        candidate_stations = list(stations)

        if user:
            # 안 본 역만 후보로
            candidate_stations = [s for s in stations if s.id not in viewed_station_ids]
            if not candidate_stations:
                candidate_stations = list(stations)  # 없으면 전체

        # 랜덤으로 역 선택 후 에피소드 가져오기
        random_station = random.choice(candidate_stations)
        ep = get_episode(random_station.id)
        if ep:
            return redirect('episode_detail', episode_id=ep.id)

    # 10️⃣ 역 상태 표시 (마커 색상, 클릭 가능 여부)
    station_list = []
    for s in stations:
        station_list.append({
            'id': s.id,
            'name': s.station_name,
            'clickable': bool(user),
            'color': 'green' if user and s.id in viewed_station_ids else 'gray'
        })

    # 11️⃣ 템플릿으로 context 전달
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

    # 1️⃣ 최근 본 에피소드 (최대 10개)
    recent_views = UserViewedEpisode.objects.filter(
        user=user
    ).select_related(
        'episode', 'episode__station'
    ).order_by('-viewed_at')[:10]

    # 2️⃣ 북마크한 에피소드
    bookmarked_episodes = Bookmark.objects.filter(
        user=user
    ).select_related(
        'episode', 'episode__station'
    ).order_by('-created_at')

    # 3️⃣ 최근 본/북마크 개수
    recent_count = recent_views.count()
    bookmark_count = bookmarked_episodes.count()

    # 4️⃣ 유저가 본 역 ID와 객체
    viewed_station_ids = set(
        recent_views.values_list('episode__station_id', flat=True)
    )
    viewed_stations = Station.objects.filter(id__in=viewed_station_ids)

    # 5️⃣ 템플릿으로 전달
    context = {
        'user': user,
        'recent_views': recent_views,
        'bookmarked_episodes': bookmarked_episodes,
        'recent_count': recent_count,
        'bookmark_count': bookmark_count,
        'viewed_stations': viewed_stations,
        'viewed_station_ids': viewed_station_ids,
    }
    return render(request, 'pages/mypage.html', context)

