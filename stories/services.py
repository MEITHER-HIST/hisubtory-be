import requests
import random
from django.core.files.base import ContentFile
from .models import Story, Station, StationStoryMeta

def generate_story_from_db(station_id):
    """
    DB에서 기획 데이터를 읽어와 AI 이미지를 생성하고 최종 Story로 저장합니다.
    """
    # 1. 기획 데이터(Meta) 가져오기
    try:
        meta = StationStoryMeta.objects.get(station_id=station_id)
        station = meta.station
    except StationStoryMeta.DoesNotExist:
        print(f"ID {station_id}번에 해당하는 기획 데이터가 없습니다.")
        return None

    keywords = [meta.kw_1, meta.kw_2, meta.kw_3, meta.kw_4]
    captions = [meta.cp_1, meta.cp_2, meta.cp_3, meta.cp_4]

    # 2. AI 이미지 생성 설정
    shared_seed = random.randint(1, 999999)
    style_preset = "Clean modern Korean webtoon art style, digital line art, cel-shaded, vibrant, high quality, no text"
    temp_images = []

    # 3. AI 호출 루프
    for i, kw in enumerate(keywords):
        url = f"https://image.pollinations.ai/prompt/{kw} {style_preset}?seed={shared_seed}&nologo=true"
        try:
            response = requests.get(url, timeout=60)
            if response.status_code == 200:
                img_name = f"{station.name_en}_{i+1}.png"
                temp_images.append((img_name, ContentFile(response.content)))
                print(f"✅ {i+1}번 컷 생성 완료")
        except Exception as e:
            print(f"❌ {i+1}번 컷 생성 중 오류: {e}")

    # 4. 이미지 4개가 성공했을 때만 세트로 저장
    if len(temp_images) == 4:
        new_story = Story(
            station=station,
            caption_1=captions[0],
            caption_2=captions[1],
            caption_3=captions[2],
            caption_4=captions[3]
        )
        # 이미지 필드에 파일 저장
        new_story.image_1.save(temp_images[0][0], temp_images[0][1], save=False)
        new_story.image_2.save(temp_images[1][0], temp_images[1][1], save=False)
        new_story.image_3.save(temp_images[2][0], temp_images[2][1], save=False)
        new_story.image_4.save(temp_images[3][0], temp_images[3][1], save=False)
        
        new_story.save()
        return new_story
    
    return None