from rest_framework import serializers
from .models import Episode, Cut


class CutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cut
        fields = ['id', 'image', 'caption', 'order']


class EpisodeSerializer(serializers.ModelSerializer):
    cuts = CutSerializer(many=True, read_only=True)

    class Meta:
        model = Episode
        fields = ['id', 'title', 'station', 'cuts']
