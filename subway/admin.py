from django.contrib import admin
from .models import Station, Line, StationLine

class StationAdmin(admin.ModelAdmin):
    list_display = ('station_name', 'station_code', 'is_enabled', 'image')
    list_filter = ('is_enabled', 'stationline__line__line_name')  
    search_fields = ('station_name', 'station_code')

admin.site.register(Station, StationAdmin)
admin.site.register(Line)
admin.site.register(StationLine)