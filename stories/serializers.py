from rest_framework import serializers
from django.conf import settings
import boto3
from botocore.client import Config
from .models import Webtoon, Episode, Cut

class CutSerializer(serializers.ModelSerializer):
    # ✅ 리액트(StoryScreen.tsx)의 c.image_url과 이름을 맞춥니다.
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Cut
        fields = ['cut_id', 'image', 'caption', 'cut_order', 'image_url']

    def get_image_url(self, obj):
        if not obj.image:
            return None
        
        # S3 Presigned URL 생성 (보안 및 접근성 확보)
        try:
            s3 = boto3.client(
                "s3",
                region_name=settings.AWS_S3_REGION_NAME,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                config=Config(signature_version="s3v4")
            )
            url = s3.generate_presigned_url(
                ClientMethod="get_object",
                Params={
                    "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
                    "Key": str(obj.image)
                },
                ExpiresIn=getattr(settings, "AWS_PRESIGN_EXPIRES", 600)
            )
            return url
        except Exception as e:
            # S3 설정이 없거나 로컬 환경인 경우를 대비한 대체 경로
            try:
                return obj.image.url
            except:
                return None

class EpisodeSerializer(serializers.ModelSerializer):
    # ✅ 역 이름 가져오기
    station_name = serializers.CharField(source='webtoon.station.station_name', read_only=True)
    # ✅ 리액트 EpisodeDTO.episode_title과 필드명 매칭
    episode_title = serializers.CharField(source='subtitle', read_only=True)
    # ✅ 컷 목록 포함
    cuts = CutSerializer(many=True, read_only=True)

    class Meta:
        model = Episode
        fields = [
            'episode_id', 
            'webtoon_id', 
            'episode_num', 
            'episode_title', # subtitle 대신 사용
            'station_name', 
            'history_summary', 
            'source_url', 
            'cuts'
        ]

# 다른 파일(views.py 등)에서 참조하는 이름 유지
StorySerializer = EpisodeSerializer

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