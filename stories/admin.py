from django.contrib import admin
from .models import Episode, Cut

# Cut Inline
class CutInline(admin.TabularInline):
    model = Cut
    extra = 1
    fields = ('image', 'caption', 'order')
    readonly_fields = ()

@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    list_display = ('get_station', 'get_webtoon_title', 'episode_num', 'subtitle', 'is_published')
    list_filter = ('station', 'is_published')  # Station FK 직접 사용
    search_fields = ('webtoon__title', 'subtitle', 'station__station_name')  # Station 이름 검색 가능
    inlines = [CutInline]

    fields = (
        'webtoon',
        'station',  # 직접 선택 가능
        'episode_num',
        'subtitle',
        'story_text',
        'source_url',
        'is_published',
        'published_at',
    )
    readonly_fields = ()  # Station 직접 선택 가능

    # list_display callable
    def get_station(self, obj):
        return obj.station.station_name if obj.station else '-'
    get_station.short_description = 'Station'

    def get_webtoon_title(self, obj):
        return obj.webtoon.title if obj.webtoon else '-'
    get_webtoon_title.short_description = 'Webtoon Title'
