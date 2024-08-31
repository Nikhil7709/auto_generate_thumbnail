from django.db import models

# Create your models here.

class Video(models.Model):
    video_url = models.URLField()
    thumbnail_with_pixel = models.ImageField(upload_to='thumbnail_with_pixel/', blank=True, null=True)
    thumbnail_with_ratio = models.ImageField(upload_to='thumbnail_with_ratio/', blank=True, null=True)
