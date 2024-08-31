from django.db import models

# Create your models here.

class Video(models.Model):
    video_url = models.URLField()
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True)
