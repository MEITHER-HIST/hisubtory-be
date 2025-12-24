from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from subway.models import Line, Station
from library.models import UserViewedEpisode
from django.db.models import Case, When, IntegerField
from django.db.models.functions import Substr, Cast
import random

# ===========================
# 메인 API 뷰
# ===========================
def main_api_view(request):
    # 1️⃣ 노선 정보
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

    # 2️⃣ 선택된 노선 처리
    line_num = request.GET.get('line', '3')
    try:
        line_int = int(line_num)
    except ValueError:
        line_int = 3
    line_obj = Line.objects.filter(line_name=f"{line_int}호선").first()

    # 3️⃣ 선택된 노선 역 목록
    stations = Station.objects.none()
    if line_obj:
        stations = Station.objects.filter(
            stationline__line=line_obj,
            is_enabled=True
        ).distinct()

    show_random_button = stations.exists()
    user = request.user if request.user.is_authenticated else None

    # 4️⃣ 유저가 본 역 ID
    viewed_station_ids = set()
    if user:
        viewed_station_ids = set(
            UserViewedEpisode.objects.filter(user=user)
            .values_list('episode__webtoon__station_id', flat=True)
        )

    # 5️⃣ 역 리스트 가공
    station_list = []
    for s in stations:
        station_list.append({
            'id': s.id,
            'name': s.station_name,
            'clickable': bool(user),
            'color': 'green' if user and s.id in viewed_station_ids else 'gray'
        })

    data = {
        'lines': line_list,
        'selected_line': line_obj.line_name if line_obj else None,
        'stations': station_list,
        'show_random_button': show_random_button,
    }
    return JsonResponse(data)


# ===========================
# 마이페이지 API 뷰
# ===========================
@login_required
def mypage_api_view(request):
    user = request.user

    # 1️⃣ 최근 본 에피소드 (최대 10개)
    recent_views = UserViewedEpisode.objects.filter(user=user)\
        .select_related('episode', 'episode__webtoon', 'episode__webtoon__station')\
        .order_by('-viewed_at')[:10]

    # 2️⃣ 저장한 에피소드 (Bookmark 대체)
    saved_episodes = UserViewedEpisode.objects.filter(user=user, saved=True)\
        .select_related('episode', 'episode__webtoon', 'episode__webtoon__station')\
        .order_by('-saved_at')

    data = {
        'user': {
            'id': user.id,
            'username': user.username
        },
        'recent_views': [
            {
                'station': v.episode.webtoon.station.station_name,
                'webtoon': v.episode.webtoon.title,
                'episode': v.episode.subtitle or v.episode.episode_num,
                'viewed_at': v.viewed_at
            } for v in recent_views
        ],
        'saved_episodes': [
            {
                'station': s.episode.webtoon.station.station_name,
                'webtoon': s.episode.webtoon.title,
                'episode': s.episode.subtitle or s.episode.episode_num,
                'saved_at': s.saved_at
            } for s in saved_episodes
        ],
        'recent_count': recent_views.count(),
        'saved_count': saved_episodes.count(),
    }
    return JsonResponse(data)
 