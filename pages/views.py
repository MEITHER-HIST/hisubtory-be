from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from subway.models import Station, Line
from stories.models import Episode
from library.models import UserViewedEpisode, Bookmark
import random

# ===========================
# 헬퍼 함수: 에피소드 선택 로직
# ===========================
def get_episode(user, station_id, fetch_unseen=True):
    """
    특정 역의 에피소드를 가져오는 로직. 
    사용자가 로그인했다면 가급적 안 본 에피소드를 우선적으로 선택합니다.
    """
    episodes = Episode.objects.filter(webtoon__station_id=station_id)
    if user and user.is_authenticated and fetch_unseen:
        seen_ids = UserViewedEpisode.objects.filter(user=user).values_list("episode_id", flat=True)
        episodes = episodes.exclude(episode_id__in=seen_ids)

    if not episodes.exists():
        episodes = Episode.objects.filter(webtoon__station_id=station_id)

    if episodes.exists():
        return random.choice(list(episodes))
    return None

# ===========================
# HTML 뷰 (기존 템플릿 방식 유지용)
# ===========================

def episode_detail(request, episode_id):
    """에피소드 상세 페이지 HTML 렌더링"""
    episode = get_object_or_404(Episode, episode_id=episode_id)
    return render(request, 'stories/episode_detail.html', {'episode': episode})

@login_required
def mypage_view(request):
    """
    HTML 렌더링 방식의 마이페이지.
    (현재 React를 사용 중이시라면 백업용으로 유지됩니다.)
    """
    user = request.user
    recent_views = UserViewedEpisode.objects.filter(user=user).select_related(
        'episode', 'episode__webtoon__station'
    ).order_by('-viewed_at')[:10]
    
    bookmarked_episodes = Bookmark.objects.filter(user=user).select_related(
        'episode', 'episode__webtoon__station'
    ).order_by('-created_at')

    context = {
        'user': user,
        'recent_views': recent_views,
        'bookmarked_episodes': bookmarked_episodes,
        'recent_count': recent_views.count(),
        'bookmark_count': bookmarked_episodes.count(),
    }
    return render(request, 'pages/mypage.html', context)

# ===========================
# 인덱스 및 상태 확인 뷰
# ===========================

def index(request):
    """서버 상태 확인용 또는 메인 페이지 진입용"""
    return HttpResponse("HISUBTORY API SERVER RUNNING")

# ✅ 주의: main_view, get_random_episode_api 등 API 전용 로직은 
# 이미 pages/views_api.py에 전문으로 작성되어 있으므로 
# views.py에서는 중복 정의하지 않음으로써 충돌을 원천 차단합니다.