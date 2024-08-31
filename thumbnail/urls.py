from django.urls import path
from .views import upload_video, video_list

urlpatterns = [
    path('upload/', upload_video, name='upload_video'),
    path('videos/', video_list, name='video_list'),
]