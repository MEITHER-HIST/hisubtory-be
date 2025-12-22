from rest_framework import serializers
from .models import Episode

class EpisodeSerializer(serializers.ModelSerializer):
    station_name = serializers.CharField(source='station.name', read_only=True)
    station_image = serializers.ImageField(source='station.image', read_only=True)

    class Meta:
        model = Episode
        fields = ['id', 'station_name', 'station_image', 'title', 'image']