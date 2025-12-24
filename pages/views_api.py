from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from subway.models import Line, Station
from library.models import UserViewedEpisode, Bookmark
from django.db.models import Case, When, IntegerField
from django.db.models.functions import Substr, Cast


def main_api_view(request):
    lines = Line.objects.annotate(
        line_number=Cast(Substr('line_name', 1, 1), IntegerField()),
        is_active_calc=Case(
            When(line_name='3호선', then=1),
            default=0,
            output_field=IntegerField()
        )
    ).order_by(
        '-is_active_calc',
        'line_number'
    )

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
            .values_list('episode__station_id', flat=True)
        )

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


@login_required
def mypage_api_view(request):
    user = request.user

    recent_views = UserViewedEpisode.objects.filter(
        user=user
    ).select_related(
        'episode', 'episode__station'
    ).order_by('-viewed_at')[:10]

    bookmarked_episodes = Bookmark.objects.filter(
        user=user
    ).select_related(
        'episode', 'episode__station'
    ).order_by('-created_at')

    data = {
        'user': {
            'id': user.id,
            'username': user.username
        },
        'recent_views': [
            {
                'station': v.episode.station.station_name,
                'episode': v.episode.title,
                'viewed_at': v.viewed_at
            } for v in recent_views
        ],
        'bookmarked_episodes': [
            {
                'station': b.episode.station.station_name,
                'episode': b.episode.title,
                'saved_at': b.created_at
            } for b in bookmarked_episodes
        ],
        'recent_count': recent_views.count(),
        'bookmark_count': bookmarked_episodes.count(),
    }
    return JsonResponse(data) 
 