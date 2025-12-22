import io, time
from django.core.files.base import ContentFile
from django.utils import timezone
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

    episode.last_viewed_at = timezone.now()
    episode.save()
    return episode