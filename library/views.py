from django.http import JsonResponse
from .models import UserActivity
from django.shortcuts import get_object_or_404
from stories.models import Episode

def my_page_api(request):
    user = request.user
    if not user.is_authenticated:
        return JsonResponse({"error": "로그인이 필요합니다."}, status=401)

    # 1. 최근 본 역사 (updated_at 대신 last_viewed_at 사용)
    recent = UserActivity.objects.filter(user=user).order_by('-last_viewed_at')[:5]
    
    recent_data = []
    for s in recent:
        recent_data.append({
            "station_id": s.episode.station.id,
            "station": s.episode.station.name,
            # 여기도 필드명을 맞춰줍니다.
            "last_viewed": s.last_viewed_at.strftime("%Y-%m-%d %H:%M") if s.last_viewed_at else ""
        })

    # 2. 나의 이야기: 저장된 것들
    saved = UserActivity.objects.filter(user=user, is_saved=True)
    
    saved_data = []
    for s in saved:
        first_image = s.episode.images.first()
        saved_data.append({
            "station_id": s.episode.station.id,
            "station": s.episode.station.name,
            "image": first_image.image.url if first_image else None
        })

    return JsonResponse({
        "recent_stories": recent_data,
        "saved_stories": saved_data
    })
    
# 저장 함수   
def save_story_api(request, episode_id):
    if not request.user.is_authenticated:
        return JsonResponse({"message": "로그인이 필요합니다."}, status=401)

    if request.method == 'POST':
        episode = get_object_or_404(Episode, id=episode_id)
        
        # UserActivity 기록을 찾거나 없으면 생성합니다.
        activity, created = UserActivity.objects.get_or_create(
            user=request.user,
            episode=episode
        )
        
        # 저장 상태를 True로 변경
        activity.is_saved = True
        activity.save()

        return JsonResponse({"message": f"'{episode.station.name}' 이야기가 보관함에 저장되었습니다!"})
    
    return JsonResponse({"message": "잘못된 접근입니다."}, status=400)