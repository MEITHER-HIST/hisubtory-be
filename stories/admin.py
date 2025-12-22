from django.contrib import admin
<<<<<<< HEAD
from .models import Episode, EpisodeImage

class EpisodeImageInline(admin.TabularInline):
    model = EpisodeImage
    extra = 0

@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    list_display = ('id', 'station', 'episode_num', 'title')
    inlines = [EpisodeImageInline]
=======
from .models import Episode

@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    list_display = ('station', 'title', 'image')
    fields = ('station', 'title', 'image')
>>>>>>> 0d6b3f83263c69e43d272063447f5061c2759c13
