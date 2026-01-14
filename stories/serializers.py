from rest_framework import serializers
from django.conf import settings
import boto3
from botocore.client import Config
from .models import Webtoon, Episode, Cut

class CutSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    class Meta:
        model = Cut
        fields = ['cut_id', 'image', 'caption', 'cut_order', 'image_url']
    def get_image_url(self, obj):
        if not obj.image: return None
        image_path = str(obj.image)
        if image_path.startswith('http'): return image_path
        try:
            s3 = boto3.client("s3", region_name=settings.AWS_S3_REGION_NAME,
                              aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                              aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                              config=Config(signature_version="s3v4"))
            return s3.generate_presigned_url(ClientMethod="get_object",
                Params={"Bucket": settings.AWS_STORAGE_BUCKET_NAME, "Key": image_path},
                ExpiresIn=getattr(settings, "AWS_PRESIGN_EXPIRES", 600))
        except: return obj.image.url if obj.image else None

class EpisodeSerializer(serializers.ModelSerializer):
    station_name = serializers.CharField(source='webtoon.station.station_name', read_only=True)
    episode_title = serializers.CharField(source='subtitle', read_only=True)
    webtoon_title = serializers.CharField(source='webtoon.title', read_only=True)
    is_viewed = serializers.BooleanField(default=False)
    cuts = CutSerializer(many=True, read_only=True)
    class Meta:
        model = Episode
        fields = ['episode_id', 'webtoon_id', 'episode_num', 'episode_title', 'webtoon_title', 'station_name', 'history_summary', 'source_url', 'is_viewed', 'cuts']

StorySerializer = EpisodeSerializer

class WebtoonSerializer(serializers.ModelSerializer):
    thumbnail_url = serializers.SerializerMethodField()
    # ✅ 중요: 뷰에서 계산해서 넘겨줄 '읽음' 상태 필드
    is_viewed = serializers.BooleanField(default=False)

    class Meta:
        model = Webtoon
        fields = ["webtoon_id", "station", "title", "author", "thumbnail", "thumbnail_url", "summary", "created_at", "is_viewed"]

    def get_thumbnail_url(self, obj):
        try:
            if obj.thumbnail and str(obj.thumbnail).startswith('http'): return str(obj.thumbnail)
            return obj.thumbnail.url if obj.thumbnail else None
        except: return None