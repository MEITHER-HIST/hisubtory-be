from django.shortcuts import get_object_or_404
from .models import Station
import random

def station_list(request):
    line = request.GET.get('line', '3호선')
    stations = Station.objects.filter(line=line, is_enabled=True)
    return stations  # API용으로 필요하면 JsonResponse로 변경 가능

def pick_random_station(line='3호선'):
    stations = Station.objects.filter(line=line, is_enabled=True)
    return random.choice(list(stations)) if stations else None