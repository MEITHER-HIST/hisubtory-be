from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Episode
from .serializers import EpisodeSerializer
from subway.models import Station
import random

@api_view(['GET'])
def station_stories(request, station_id):
    station = get_object_or_404(Station, id=station_id)
    episodes = Episode.objects.filter(station=station)

    if episodes.exists():
        episode = random.choice(episodes)
        serializer = EpisodeSerializer(episode)
        return Response(serializer.data)
    else:
        return Response({"message": "해당 역의 스토리가 없습니다."}, status=404)