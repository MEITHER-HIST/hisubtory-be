from rest_framework import serializers
from .models import Episode, Cut

class CutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cut
        fields = ['id', 'image', 'caption', 'order']

class EpisodeSerializer(serializers.ModelSerializer):
    cuts = CutSerializer(many=True, read_only=True)
    title = serializers.SerializerMethodField()  # title 필드 직접 생성

    class Meta:
        model = Episode
        fields = ['id', 'title', 'station', 'cuts']

    def get_title(self, obj):
        # subtitle 있으면 subtitle, 없으면 "웹툰 제목 - n화"
        if obj.subtitle:
            return f"{obj.webtoon.title} - {obj.subtitle}"
        return f"{obj.webtoon.title} - {obj.episode_num}화"
