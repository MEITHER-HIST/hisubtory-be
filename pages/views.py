from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
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
    # 0) 헬스체커/루트 접근은 OK로 응답 (템플릿 미사용)
    #    - 브라우저로 열어도 200이 떠서 배포 확인용으로 좋음
    user = request.user if request.user.is_authenticated else None

    # 1) 역 클릭 처리(기존 로직 유지)
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
                    episode_id_for_redirect = last_episode.episode_id
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

            # 클릭은 했지만 에피소드 못 찾은 경우도 “반드시 응답”
            return JsonResponse({"ok": False, "reason": "no_episode"}, status=404)

        except ValueError:
            return JsonResponse({"ok": False, "reason": "invalid_station_id"}, status=400)

    # 2) 랜덤 스토리 버튼 처리(기존 로직 유지)
    if request.GET.get('random') == '1':
        line_num = request.GET.get('line', '3')
        try:
            line_int = int(line_num)
        except ValueError:
            line_int = 3

        line_obj = Line.objects.filter(line_name=f"{line_int}호선").first()
        stations = Station.objects.filter(is_enabled=True) if line_obj else Station.objects.none()

        if stations.exists():
            viewed_station_ids = set()
            if user:
                viewed_station_ids = set(
                    UserViewedEpisode.objects.filter(user=user)
                    .values_list("episode__webtoon__station_id", flat=True)
                )

            candidate_stations = list(stations)
            if user:
                candidate_stations = [s for s in stations if s.id not in viewed_station_ids] or list(stations)

            random_station = random.choice(candidate_stations)
            ep = get_episode(user, random_station.id)
            if ep:
                return redirect('episode_detail', episode_id=ep.episode_id)

        return JsonResponse({"ok": False, "reason": "no_station_or_episode"}, status=404)

    # 3) 그냥 / 접근은 OK로 응답 (템플릿 대신)
    return HttpResponse("OK")


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