from django.contrib import admin

# Register your models here.

from thumbnail.models import Video

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('video_url', 'thumbnail_with_pixel', 'thumbnail_with_ratio',)
    search_fields = ('video_url',)
    list_filter = ('thumbnail_with_pixel', 'thumbnail_with_ratio',)