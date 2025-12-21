# stories/services.py
import requests
from django.core.files.base import ContentFile
from django.conf import settings

# 무료 AI 모델 URL (예: Stable Diffusion)
API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
# 무료 토큰이 있다면 여기 입력 (없어도 테스트 가능하지만 횟수 제한이 있을 수 있음)
HEADERS = {"Authorization": f"Bearer {getattr(settings, 'HUGGINGFACE_TOKEN', '')}"}

def generate_episode_image_service(episode_instance):
    """
    에피소드의 요약본을 바탕으로 AI 이미지를 생성하여 source_url에 저장하는 서비스
    """
    if not episode_instance.history_summary:
        print("⚠️ 요약 내용이 없어 이미지를 생성하지 않습니다.")
        return None

    # 프롬프트 구성
    prompt = f"Historical scene of {episode_instance.station.name}: {episode_instance.history_summary}. cinematic, highly detailed, historical masterpiece."
    
    try:
        # AI API 호출
        response = requests.post(API_URL, headers=HEADERS, json={"inputs": prompt}, timeout=30)
        
        if response.status_code == 200:
            # 이미지 데이터를 ContentFile로 변환하여 저장
            filename = f"ai_gen_{episode_instance.id}.jpg"
            episode_instance.source_url.save(filename, ContentFile(response.content), save=True)
            print(f"✅ [Service] AI 이미지 생성 및 저장 성공: {episode_instance.source_url.name}")
            return episode_instance.source_url.url
        else:
            print(f"❌ [Service] API 호출 실패: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ [Service] 서버 에러 발생: {e}")
        return None