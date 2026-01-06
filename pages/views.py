from django.shortcuts import render, get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.decorators import login_required
from subway.models import Station, Line
from stories.models import Episode
from library.models import UserViewedEpisode, Bookmark
from django.db.models import IntegerField, Case, When
from django.db.models.functions import Cast, Substr
import random

# ===========================
# 헬퍼 함수: 에피소드 선택 로직
# ===========================
def get_episode(user, station_id, fetch_unseen=True):
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
# HTML 뷰 (URL 충돌 방지용)
# ===========================
def episode_detail(request, episode_id):
    episode = get_object_or_404(Episode, episode_id=episode_id)
    return render(request, 'stories/episode_detail.html', {'episode': episode})

@login_required
def mypage_view(request):
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
# 메인 화면 API
# ===========================
@api_view(['GET'])
@permission_classes([AllowAny])
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
        line_list.append({
            'id': line.id,
            'line_name': line.line_name + ('' if is_active else ' (준비중)'),
            'is_active': is_active
        })

    stations = Station.objects.filter(is_enabled=True)
    user = request.user if request.user.is_authenticated else None
    viewed_station_ids = set()
    if user:
        viewed_station_ids = set(
            UserViewedEpisode.objects.filter(user=user)
            .values_list("episode__webtoon__station_id", flat=True)
        )

    station_list = []
    for s in stations:
        is_viewed = user is not None and (s.id in viewed_station_ids)
        station_list.append({
            'id': s.id,
            'name': s.station_name,
            'clickable': True,
            'color': 'green' if is_viewed else 'gray',
            'is_viewed': is_viewed
        })

    return Response({
        "success": True,
        "lines": line_list,
        "stations": station_list,
        "show_random_button": stations.exists(),
    })

# ===========================
# 에피소드 랜덤 추천 API
# ===========================
@api_view(['GET'])
@permission_classes([AllowAny])
def get_random_episode_api(request):
    # 1. 에피소드가 존재하는 모든 웹툰의 역 ID 목록을 가져옵니다.
    # SQL 결과에서 보듯 station_id 2, 3, 4, 5, 6 등이 후보가 됩니다.
    station_ids_with_eps = Episode.objects.values_list('webtoon__station_id', flat=True).distinct()
    
    if not station_ids_with_eps:
        return Response({"success": False, "message": "에피소드가 연결된 역이 DB에 하나도 없습니다."}, status=404)

    # 2. 해당 역 ID들 중에서 랜덤으로 하나를 선택합니다.
    random_station_id = random.choice(list(station_ids_with_eps))
    
    # 3. 선택된 역 정보와 에피소드를 가져옵니다.
    station = Station.objects.filter(id=random_station_id).first()
    ep = Episode.objects.filter(webtoon__station_id=random_station_id).first()

    if station and ep:
        return Response({
            "success": True,  # ✅ 리액트의 if(data.success) 조건을 위해 반드시 필요
            "episode_id": ep.episode_id,
            "station_name": station.station_name,
            "station_id": station.id # 추가 정보
        })
    
    return Response({"success": False, "message": "에피소드를 찾지 못했습니다."}, status=404)