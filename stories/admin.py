from django.contrib import admin
from .models import Webtoon, Episode, Cut, StoriesEpisode

@admin.register(Webtoon)
class WebtoonAdmin(admin.ModelAdmin):
    list_display = ('webtoon_id', 'station', 'title', 'author')

@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    # 📌 station_id 대신 webtoon을 표시
    list_display = ('episode_id', 'webtoon', 'episode_num', 'subtitle', 'is_published')
    # 📌 필터링도 관계 필드인 webtoon__station을 사용
    list_filter = ('webtoon__station', 'is_published')
    search_fields = ('subtitle',)

@admin.register(Cut)
class CutAdmin(admin.ModelAdmin):
    list_display = ('cut_id', 'episode', 'cut_order')

@admin.register(StoriesEpisode)
class StoriesEpisodeAdmin(admin.ModelAdmin):
    # 📌 여기는 station_id(fk)가 있으므로 사용 가능
    list_display = ('id', 'station', 'title', 'episode_num')