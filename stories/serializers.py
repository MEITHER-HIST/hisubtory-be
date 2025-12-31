from rest_framework import serializers
from django.conf import settings
import boto3
from botocore.client import Config
from .models import Webtoon, Episode, Cut

class CutSerializer(serializers.ModelSerializer):
    # DB에 저장된 이미지 경로를 S3 보안 URL로 변환하기 위한 필드
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Cut
        fields = ["cut_id", "cut_order", "image", "image_url", "caption", "created_at"]
        read_only_fields = ["cut_id", "created_at"]
        extra_kwargs = {
            "image": {"write_only": True},
            "caption": {"required": True, "allow_blank": False},
        }

    def validate_caption(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("caption은 필수입니다.")
        return value

    def validate_cut_order(self, value):
        if not (1 <= value <= 4):
            raise serializers.ValidationError("cut_order는 1~4만 가능합니다.")
        return value

    def get_image_url(self, obj):
        if not obj.image:
            return None

        # S3 클라이언트 설정 (우리가 구현한 보안 URL 생성 로직 유지)
        try:
            s3 = boto3.client(
                "s3",
                region_name=settings.AWS_S3_REGION_NAME,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                config=Config(signature_version="s3v4"),
            )
            return s3.generate_presigned_url(
                ClientMethod="get_object",
                Params={
                    "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
                    "Key": obj.image.name,
                },
                ExpiresIn=getattr(settings, "AWS_PRESIGN_EXPIRES", 600),
            )
        except Exception:
            # S3 설정 미비 시 대체 경로 반환
            return obj.image.url if hasattr(obj.image, 'url') else None

class EpisodeSerializer(serializers.ModelSerializer):
    # 에피소드에 연결된 컷들을 가져옴
    cuts = CutSerializer(many=True, read_only=True)

    class Meta:
        model = Episode
        fields = [
            "episode_id", "webtoon", "episode_num", "subtitle",
            "history_summary", "source_url",
            "is_published", "published_at", "created_at",
            "cuts"
        ]

# 팀원 코드에서 'StorySerializer'라는 이름을 사용할 경우를 대비해 별칭 설정
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