from rest_framework import serializers
from .models import Episode, Cut

# 컷용 Serializer
class CutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cut
        fields = ['id', 'image_url', 'description']  # 필요한 필드만 넣어

# 에피소드 Serializer
class EpisodeSerializer(serializers.ModelSerializer):
    cuts = serializers.SerializerMethodField()  # 커스텀 필드 추가

    class Meta:
        model = Episode
        fields = '__all__'  # 기존 필드는 그대로
        # 또는 필요한 필드만 명시 가능: ['id', 'title', 'station', 'cuts']

    # 컷 4개만 반환
    def get_cuts(self, obj):
        return CutSerializer(obj.cuts.all()[:4], many=True).data
