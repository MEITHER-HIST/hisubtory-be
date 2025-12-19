import requests
import random
from django.core.files.base import ContentFile
from django.utils import timezone
from .models import Episode
from subway.models import Station

def get_or_generate_episode_logic():
    # 1. 랜덤 역 선택
    stations = Station.objects.all()
    if not stations.exists(): return None
    target_station = random.choice(stations)

    # 2. 순환 로직: 안 본 것 우선 -> 가장 오래전에 본 것 순서
    episode = Episode.objects.filter(station=target_station).order_by('last_viewed_at').first()

    if not episode: return None

    # 3. 이미지 캐싱: 이미지가 없으면 신규 생성
    if not episode.source_url:
        style_preset = (
            "Clean modern Korean webtoon art style, digital line art, cel-shaded, "
            "vibrant colors, high quality, consistent character design, no text"
        )
        prompt = f"{episode.subtitle} {style_preset}"
        seed = episode.id + 1000
        api_url = f"https://image.pollinations.ai/prompt/{prompt}?seed={seed}&nologo=true&width=1024&height=1024"

        try:
            response = requests.get(api_url, timeout=60)
            if response.status_code == 200:
                filename = f"st{target_station.id}_ep{episode.episode_num}.png"
                # 생성된 이미지를 source_url 필드에 저장
                episode.source_url.save(filename, ContentFile(response.content), save=False)
        except Exception as e:
            print(f"생성 실패: {e}")
            return None

    # 4. 노출 시간 업데이트 (순환을 위해 현재 시간 기록)
    episode.last_viewed_at = timezone.now()
    episode.save()

    return episode