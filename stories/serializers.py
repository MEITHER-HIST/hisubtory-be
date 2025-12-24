from rest_framework import serializers
from django.conf import settings
import boto3
from botocore.client import Config

from .models import Webtoon, Episode, Cut

class CutSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Cut
        fields = ["cut_id", "cut_order", "image", "image_url", "caption", "created_at"]
        read_only_fields = ["cut_id", "created_at"]
        extra_kwargs = {
            "image": {"write_only": True},           # 업로드만 받고 응답에는 안 줌
            "caption": {"required": True, "allow_blank": False},  # POST에서 필수 + 빈문자열 금지
        }

    def validate_caption(self, value: str):
        # "   " 같은 공백 캡션도 막기
        if value is None or not value.strip():
            raise serializers.ValidationError("caption은 필수입니다.")
        return value

    def get_image_url(self, obj):
        if not obj.image:
            return None

        # 핵심: obj.image.name 을 S3 Key로 써야 함 (url 말고 name)
        key = obj.image.name

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
                "Key": key,
            },
            ExpiresIn=getattr(settings, "AWS_PRESIGN_EXPIRES", 600),  # 기본 10분
        )

    def validate_cut_order(self, value):
        if not (1 <= value <= 4):
            raise serializers.ValidationError("cut_order는 1~4만 가능합니다.")
        return value

class EpisodeSerializer(serializers.ModelSerializer):
    cuts = CutSerializer(many=True, read_only=True)

    class Meta:
        model = Episode
        fields = [
            "episode_id", "webtoon", "episode_num", "subtitle",
            "history_summary", "source_url",
            "is_published", "published_at", "created_at",
            "cuts"
        ]

class WebtoonSerializer(serializers.ModelSerializer):
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = Webtoon
        fields = ["webtoon_id", "station", "title", "author", "thumbnail", "thumbnail_url", "summary", "created_at"]
        extra_kwargs = {"thumbnail": {"write_only": True}}

    def get_thumbnail_url(self, obj):
        return obj.thumbnail.url if obj.thumbnail else None
