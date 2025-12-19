import requests
import random
from django.core.files.base import ContentFile
from django.utils import timezone
from .models import Episode, Station

def get_or_generate_episode_logic():
    # 1. 랜덤 역 선택
    stations = Station.objects.all()
    if not stations.exists():
        return None
    target_station = random.choice(stations)

    # 2. 순환 로직: 미시청 에피소드 우선 -> 가장 오래전에 본 순서
    episode = Episode.objects.filter(station=target_station).order_by('last_viewed_at').first()

    if not episode:
        return None

    # 3. 이미지 생성 (시드 고정으로 화풍 유지)
    if not episode.source_url:
        # 에피소드 ID를 시드로 활용하여 일관성 확보
        fixed_seed = episode.id + 777 
        style_preset = "Clean modern Korean webtoon art style, digital line art, cel-shaded, vibrant, high quality"
        prompt = f"{episode.subtitle}, {style_preset}"
        
        api_url = f"https://image.pollinations.ai/prompt/{prompt}?seed={fixed_seed}&nologo=true"

        try:
            response = requests.get(api_url, timeout=60)
            if response.status_code == 200:
                filename = f"st{target_station.id}_ep{episode.episode_num}.png"
                # DB 필드에 파일 저장
                episode.source_url.save(filename, ContentFile(response.content), save=False)
        except Exception as e:
            print(f"생성 중 오류 발생: {e}")
            return None

    # 4. 마지막 노출 시간 갱신 (순환의 핵심)
    episode.last_viewed_at = timezone.now()
    episode.save()

    return episode