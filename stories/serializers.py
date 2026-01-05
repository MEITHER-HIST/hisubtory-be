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
        # 1. 데이터가 없는 경우
        if not obj.image:
            return None
        
        # 2. ✅ 핵심 수정: 이미 전체 URL(https://...)이 들어있는 경우 그대로 반환
        # CloudFront 주소 등이 DB에 직접 저장된 경우 Presigned URL 생성이 필요 없습니다.
        image_path = str(obj.image)
        if image_path.startswith('http'):
            return image_path
        
        # 3. 상대 경로(media/...)인 경우에만 S3 Presigned URL 생성
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
                    "Key": image_path
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
            # 썸네일도 URL 형태라면 바로 반환하도록 예외 처리 가능
            if obj.thumbnail and str(obj.thumbnail).startswith('http'):
                return str(obj.thumbnail)
            return obj.thumbnail.url if obj.thumbnail else None
        except Exception:
            return None