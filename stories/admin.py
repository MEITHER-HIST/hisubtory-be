from django.contrib import admin
from .models import Webtoon, Episode, Cut

@admin.register(Webtoon)
class WebtoonAdmin(admin.ModelAdmin):
    list_display = ('webtoon_id', 'station', 'title', 'author', 'created_at')
    list_filter = ('station',)
    search_fields = ('title', 'author')

# Cut 모델을 에피소드 수정 페이지에서 바로 볼 수 있게 하는 Inline 설정
class CutInline(admin.TabularInline):
    model = Cut
    extra = 1
    # [주의] 'order' 필드가 DB에 없으면 'id'로 변경하거나 제외해야 합니다.
    fields = ('image', 'caption') 

@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    # [수정] 우리 모델의 실제 필드명(station_id, title 등)으로 맞춤
    list_display = ("id", "station_id", "title", "episode_num", "subtitle", "last_viewed_at")
    list_filter = ("station_id", "episode_num")
    search_fields = ("title", "subtitle", "history_summary")
    inlines = [CutInline]  # 에피소드 상세 페이지에서 컷들을 바로 관리 가능

@admin.register(Cut)
class CutAdmin(admin.ModelAdmin):
    # [수정] 실제 존재하는 필드만 노출
    list_display = ('id', 'episode', 'caption')
    list_filter = ('episode',)
    ordering = ('episode', 'id')