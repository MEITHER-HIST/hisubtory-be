from rest_framework import serializers
from .models import Webtoon, Episode, Cut

class CutSerializer(serializers.ModelSerializer):
    # DB에 저장된 이미지 경로를 안전하게 가져오기 위한 필드
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Cut
        # DB 스샷 기반: id, image, caption 필드 반영
        fields = ['id', 'image', 'image_url', 'caption']

    def get_image_url(self, obj):
        try:
            # S3 설정이 되어있다면 S3 URL을, 아니라면 저장된 경로를 반환합니다.
            return obj.image.url if obj.image else None
        except Exception:
            # 필드 형태가 CharField일 경우를 대비한 예외 처리
            return str(obj.image) if obj.image else None

# views.py에서 'StorySerializer'라는 이름으로 호출하므로 이름을 맞춥니다.
class StorySerializer(serializers.ModelSerializer):
    cuts = CutSerializer(many=True, read_only=True)

    class Meta:
        model = Episode
        # DB 스샷 및 models.py 구성 기반 필드 목록
        fields = [
            "id", 
            "station_id",   # station 대신 실제 컬럼명인 station_id 반영
            "title", 
            "episode_num", 
            "subtitle",
            "history_summary", 
            "source_url", 
            "last_viewed_at",
            "cuts"
        ]

# 혹시 몰라 기존에 쓰던 EpisodeSerializer 이름도 StorySerializer와 연결해둡니다.
EpisodeSerializer = StorySerializer

class WebtoonSerializer(serializers.ModelSerializer):
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = Webtoon
        fields = [
            "webtoon_id", "station", "title", "author", 
            "thumbnail", "thumbnail_url", "summary", "created_at"
        ]
        extra_kwargs = {"thumbnail": {"write_only": True}}

    def get_thumbnail_url(self, obj):
        try:
            return obj.thumbnail.url if obj.thumbnail else None
        except Exception:
            return None