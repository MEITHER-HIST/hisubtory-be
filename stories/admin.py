from django.contrib import admin
from .models import Episode
from subway.models import Station # Station 모델도 등록해두면 편리합니다.

@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    list_display = ('id', 'station', 'episode_num', 'subtitle', 'history_summary', 'source_url')
    list_filter = ('station',)
    search_fields = ('subtitle', 'history_summary', 'station__name') # 아까 고친 'name' 사용

@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)