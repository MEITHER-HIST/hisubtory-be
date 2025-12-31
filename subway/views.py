from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from urllib.parse import unquote  # 한글 깨짐 방지
import logging
from .models import Story
from .serializers import StorySerializer

class StationStoryView(APIView):
    def get(self, request, station_identifier):
        # 1. 한글 복원
        decoded_name = unquote(station_identifier)
        print(f"DEBUG: 요청받은 식별자: {decoded_name}") # 터미널 확인용

        try:
            # 2. 숫자인 경우 ID로 검색
            if decoded_name.isdigit():
                story = get_object_or_404(Story, station_id=decoded_name)
            else:
                # 3. 문자인 경우 이름으로 검색
                # 주의: station__station_name 이 실제 모델 필드명과 일치해야 함
                story = get_object_or_404(Story, station__station_name=decoded_name)
            
            serializer = StorySerializer(story)
            return Response(serializer.data)
            
        except Exception as e:
            print(f"DEBUG 에러 발생: {e}")
            return Response({"error": str(e)}, status=404)