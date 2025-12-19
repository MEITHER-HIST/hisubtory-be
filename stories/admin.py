from django.contrib import admin
from .models import Episode  # Story 대신 Episode를 가져옵니다.

@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    # 관리자 목록 화면에서 보여줄 필드 설정
    list_display = ('id', 'station', 'episode_num', 'subtitle', 'last_viewed_at')
    
    # 클릭해서 상세 페이지로 들어갈 수 있는 링크 설정
    list_display_links = ('id', 'subtitle')
    
    # 역 이름으로 검색할 수 있는 기능 추가
    search_fields = ('station__station_name', 'subtitle')
    
    # 특정 역별로 필터링해서 볼 수 있는 기능 추가
    list_filter = ('station',)