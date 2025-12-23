from django.contrib import admin
from .models import Episode

@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    list_display = ('station', 'title', 'image')
    fields = ('station', 'title', 'image')