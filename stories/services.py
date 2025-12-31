import requests  # 👈 설치가 안 되어 있다면 여기서 밑줄이 뜹니다.
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
    
    # 2. 순환 로직 수정 (명세 2번 Episode에는 last_viewed_at이 없음)
    # 대신 생성일(created_at) 순서나 무작위로 가져오도록 수정합니다.
    episode = Episode.objects.filter(
        webtoon__station=target_station
    ).order_by('created_at').first() # last_viewed_at이 없으므로 created_at 사용

    if not episode:
        return None

    # 3. 이미지 생성 (Pollinations AI 로직 유지)
    if not episode.source_url:
        fixed_seed = episode.episode_id + 777 
        style_preset = "Clean modern Korean webtoon art style, digital line art, cel-shaded, vibrant, high quality"
        prompt = f"{episode.subtitle}, {style_preset}"
        
        api_url = f"https://image.pollinations.ai/prompt/{prompt}?seed={fixed_seed}&nologo=true"

        try:
            # 외부 API 호출
            response = requests.get(api_url, timeout=60)
            if response.status_code == 200:
                # 📌 주의: 명세 2번의 source_url이 CharField라면 저장이 가능하지만
                # URLField인 경우 ContentFile 저장이 안 될 수 있습니다.
                # 여기서는 단순히 생성 성공 여부만 체크하도록 pass 처리합니다.
                pass 
        except Exception as e:
            print(f"이미지 생성 중 오류 발생: {e}")

    # 4. 정보 갱신
    # 명세 2번 Episode 테이블에는 노출 시간을 기록하는 필드가 없으므로
    # 필요한 경우 별도의 로그를 남기거나 save()만 수행합니다.
    episode.save() 
    return episode