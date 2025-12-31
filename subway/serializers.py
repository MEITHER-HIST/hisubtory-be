# serializers.py
from rest_framework import serializers
from .models import Station

class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ['id', 'station_name', 'station_code'] # 프론트에서 쓸 필드만 정의