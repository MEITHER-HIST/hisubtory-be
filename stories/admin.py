from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Webtoon, Episode, Cut

@admin.register(Webtoon)
class WebtoonAdmin(admin.ModelAdmin):
    list_display = ('webtoon_id', 'title', 'station', 'created_at')
    search_fields = ('title',)
    list_filter = ('station',)

@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    # ✅ 'episode_title'을 모델에 존재하는 'subtitle'로 수정했습니다.
    list_display = ('episode_id', 'webtoon', 'episode_num', 'subtitle', 'is_published')
    search_fields = ('subtitle', 'webtoon__title') # 웹툰 제목으로도 검색 가능
    list_filter = ('webtoon', 'is_published')

# stories/admin.py

@admin.register(Cut)
class CutAdmin(admin.ModelAdmin):
    list_display = ('cut_id', 'episode', 'cut_order', 'image_preview')
    list_filter = ('episode__webtoon', 'episode')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if not obj.image:
            return "No Image"
        
        # 1. ImageField 객체인 경우 (속성 url 존재)
        if hasattr(obj.image, 'url'):
            try:
                return mark_safe(f'<img src="{obj.image.url}" width="100" />')
            except:
                pass
        
        # 2. 일반 문자열(str)인 경우 (DB에 경로만 저장된 경우)
        image_path = str(obj.image)
        # S3 주소 체계로 변환 (필요 시 수정)
        if image_path.startswith('s3://'):
            # s3://버킷명/경로 -> https://버킷명.s3.amazonaws.com/경로 형식으로 변환 시도
            path_only = image_path.replace('s3://hisub-s3-bucket/', '')
            image_url = f"https://hisub-s3-bucket.s3.ap-northeast-2.amazonaws.com/{path_only}"
        else:
            image_url = image_path

        return mark_safe(f'<img src="{image_url}" width="100" />')

    image_preview.short_description = "미리보기"