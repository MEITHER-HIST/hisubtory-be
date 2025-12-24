from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from subway.models import Line, Station
from library.models import UserViewedEpisode, Bookmark
from django.db.models import Case, When, IntegerField
from django.db.models.functions import Substr, Cast

# ===========================
# 메인 API 뷰: /main/ 관련 데이터 제공
# ===========================
def main_api_view(request):
    # 1️⃣ 노선 정보를 가져오고 정렬
    # line_number: 노선 이름의 첫 글자를 숫자로 변환 (1호선, 2호선 등)
    # is_active_calc: '3호선'만 활성화로 표시, 나머지는 비활성
    lines = Line.objects.annotate(
        line_number=Cast(Substr('line_name', 1, 1), IntegerField()),
        is_active_calc=Case(
            When(line_name='3호선', then=1),
            default=0,
            output_field=IntegerField()
        )
    ).order_by(
        '-is_active_calc',  # 3호선 먼저
        'line_number'       # 그 다음 숫자 순
    )

    # 2️⃣ 프론트에 보낼 리스트 생성
    line_list = []
    for line in lines:
        is_active = bool(line.is_active_calc)  # 활성화 여부 True/False

        display_name = line.line_name
        if not is_active:
            display_name += ' (준비중)'  # 비활성 노선 표시

        line_list.append({
            'id': line.id,
            'line_name': display_name,
            'is_active': is_active
        })

    # 3️⃣ 선택된 노선 파라미터 처리 (GET ?line=3)
    line_num = request.GET.get('line', '3')  # 기본 3호선
    try:
        line_int = int(line_num)
    except ValueError:
        line_int = 3  # 숫자가 아니면 3으로 기본값

    # 선택된 Line 객체 가져오기
    line_obj = Line.objects.filter(line_name=f"{line_int}호선").first()

    # 4️⃣ 선택된 노선의 역 목록 가져오기
    stations = Station.objects.none()
    if line_obj:
        stations = Station.objects.filter(
            stationline__line=line_obj,  # 해당 노선 소속 역
            is_enabled=True              # 활성화된 역만
        ).distinct()

    # 5️⃣ 랜덤 버튼 표시 여부 (역이 하나라도 있으면 True)
    show_random_button = stations.exists()

    # 6️⃣ 로그인 유저 확인
    user = request.user if request.user.is_authenticated else None

    # 7️⃣ 유저가 본 역 ID 가져오기
    viewed_station_ids = set()
    if user:
        # UserViewedEpisode에서 에피소드 기준으로 역 ID 추출
        viewed_station_ids = set(
            UserViewedEpisode.objects.filter(user=user)
            .values_list('episode__station_id', flat=True)
        )

    # 8️⃣ 역 정보를 프론트에 맞는 형태로 가공
    station_list = []
    for s in stations:
        station_list.append({
            'id': s.id,
            'name': s.station_name,
            'clickable': bool(user),  # 로그인 유저만 클릭 가능
            'color': 'green' if user and s.id in viewed_station_ids else 'gray'  # 색상 표시
        })

    # 9️⃣ JSON 데이터 구성 후 반환
    data = {
        'lines': line_list,
        'selected_line': line_obj.line_name if line_obj else None,
        'stations': station_list,
        'show_random_button': show_random_button,
    }
    return JsonResponse(data)


# ===========================
# 마이페이지 API 뷰: 로그인 유저 최근본 에피, 북마크 제공
# ===========================
@login_required
def mypage_api_view(request):
    user = request.user

    # 1️⃣ 최근 본 에피소드 가져오기 (최대 10개)
    recent_views = UserViewedEpisode.objects.filter(
        user=user
    ).select_related(
        'episode', 'episode__station'
    ).order_by('-viewed_at')[:10]

    # 2️⃣ 유저가 북마크한 에피소드 가져오기
    bookmarked_episodes = Bookmark.objects.filter(
        user=user
    ).select_related(
        'episode', 'episode__station'
    ).order_by('-created_at')

    # 3️⃣ 프론트에 맞는 JSON 데이터 구성
    data = {
        'user': {
            'id': user.id,
            'username': user.username
        },
        'recent_views': [
            {
                'station': v.episode.station.station_name,  # 역 이름
                'episode': v.episode.title,                # 에피소드 제목
                'viewed_at': v.viewed_at                   # 본 시간
            } for v in recent_views
        ],
        'bookmarked_episodes': [
            {
                'station': b.episode.station.station_name, # 역 이름
                'episode': b.episode.title,               # 에피소드 제목
                'saved_at': b.created_at                  # 북마크 시간
            } for b in bookmarked_episodes
        ],
        'recent_count': recent_views.count(),          # 최근 본 에피 갯수
        'bookmark_count': bookmarked_episodes.count(),# 북마크 갯수
    }
    return JsonResponse(data)
