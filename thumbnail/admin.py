from django.contrib import admin

# Register your models here.
# Register your models here.

from thumbnail.models import Video

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('video_url', 'thumbnail')
    search_fields = ('video_url',)
    list_filter = ('thumbnail',)