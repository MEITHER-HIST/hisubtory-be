import io, time
from django.core.files.base import ContentFile
from django.utils import timezone
<<<<<<< HEAD
from huggingface_hub import InferenceClient
from django.conf import settings
from .models import Episode, EpisodeImage

def generate_four_images_service(episode_instance):
    token = getattr(settings, 'HUGGINGFACE_TOKEN', None)
    client = InferenceClient(api_key=token)
    model_id = "stabilityai/stable-diffusion-xl-base-1.0"
    
    if episode_instance.images.count() >= 4:
        return episode_instance.images.all()

    # 구도를 다르게 잡기 위한 프롬프트 리스트
    prompts = [
        f"A historical wide shot of {episode_instance.station.name} in 1920s, oil painting style",
        f"Close up of {episode_instance.station.name} architectural detail, 1920s style, oil painting",
        f"Vintage steam engine train at {episode_instance.station.name} platform, 1920s, oil painting",
        f"People in 1920s Seoul fashion walking near {episode_instance.station.name}, oil painting"
    ]

    for i, p in enumerate(prompts, 1):
        try:
            print(f"🔄 {i}번째 이미지 생성 중...")
            image = client.text_to_image(p, model=model_id)
            
            buffer = io.BytesIO()
            image.save(buffer, format="PNG")
            
            # EpisodeImage 객체 생성
            new_img = EpisodeImage(
                episode=episode_instance,
                caption=f"{episode_instance.station.name}의 풍경 {i}"
            )
            new_img.image.save(f"ep{episode_instance.id}_{i}_{int(time.time())}.png", ContentFile(buffer.getvalue()), save=True)
            time.sleep(1) # API 안정성을 위한 짧은 휴식
        except Exception as e:
            print(f"❌ {i}번째 생성 실패 상세 에러: {e}") # 이렇게 수정해서 다시 실행해 보세요.

    return episode_instance.images.all()

def get_next_episode_with_ai_service(user, station_id):
    episode = Episode.objects.filter(station_id=station_id).order_by('last_viewed_at').first()
    if not episode: return None

    # [수정] 이미지가 4개 미만이면 생성 함수 호출
    if episode.images.count() < 4:
        generate_four_images_service(episode)

=======
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
>>>>>>> 0d6b3f83263c69e43d272063447f5061c2759c13
    episode.last_viewed_at = timezone.now()
    episode.save()
    return episode