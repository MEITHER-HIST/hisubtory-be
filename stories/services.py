import requests
import random
from django.core.files.base import ContentFile
from django.utils import timezone
from .models import Episode, Station, Webtoon

def get_or_generate_episode_logic():
    # 1. 랜덤 역 선택
    stations = Station.objects.filter(is_enabled=True)
    if not stations.exists():
        return None
    target_station = random.choice(stations)
    
    # 2. 순환 로직: 해당 역과 연관된 웹툰의 에피소드 중 가장 오래전에 본 순서
    # DB 명세: Station(1) -> Webtoon(N) -> Episode(N)
    episode = Episode.objects.filter(
        webtoon__station=target_station
    ).order_by('last_viewed_at').first()

    if not episode:
        return None

    # 3. 이미지 생성 (Pollinations AI 로직 유지)
    # 명세에 따라 source_url이 CharField/URLField일 수 있으므로 유연하게 처리
    if not episode.source_url:
        # 수정된 PK 필드명(episode_id)을 시드로 활용
        fixed_seed = episode.episode_id + 777 
        style_preset = "Clean modern Korean webtoon art style, digital line art, cel-shaded, vibrant, high quality"
        prompt = f"{episode.subtitle}, {style_preset}"
        
        api_url = f"https://image.pollinations.ai/prompt/{prompt}?seed={fixed_seed}&nologo=true"

        try:
            response = requests.get(api_url, timeout=60)
            if response.status_code == 200:
                # 필드 타입에 따라 처리 (ImageField인 경우 .save() 사용, 아니면 경로 저장)
                # 현재 명세 2번에서는 source_url이 출처 링크용이므로, 
                # 만약 이미지를 저장해야 한다면 별도의 ImageField가 필요할 수 있습니다.
                # 여기서는 기존 로직대로 에러 없이 동작하도록 구성했습니다.
                pass 
        except Exception as e:
            print(f"이미지 생성 중 오류 발생: {e}")
            # 생성 실패해도 로직은 계속 진행

    # 4. 마지막 노출 시간 갱신 (순환의 핵심)
    episode.last_viewed_at = timezone.now()
    episode.save(update_fields=['last_viewed_at'])
    return episode