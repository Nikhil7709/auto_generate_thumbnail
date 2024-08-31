import os
from django.http import HttpResponseBadRequest
from django.shortcuts import render, redirect
from .forms import VideoForm
from .models import Video
from .utils import capture_screenshot, download_video

from django.core.files.base import ContentFile
from django.conf import settings
import io


def upload_video(request):
    """
    Handles video upload and thumbnail generation and saves the thumbnail.
    If the timestamp is invalid, generates a random thumbnail.
    """
    if request.method == 'POST':
        form = VideoForm(request.POST)
        timestamp_str = request.POST.get('timestamp', None)
        timestamp = None
        
        if timestamp_str:
            try:
                timestamp = float(timestamp_str)
            except ValueError:
                return HttpResponseBadRequest("Invalid timestamp format.")
        
        if form.is_valid():
            video = form.save(commit=False)
            video_file = download_video(video.video_url)
            if video_file:
                try:
                    # Capture and resize the screenshot and get the video duration
                    thumbnail_io, video_duration, screenshot_time = capture_screenshot(video_file, timestamp)
                    
                    # Format filename with timestamp if available
                    thumbnail_filename = f'thumbnail_{screenshot_time:.2f}.jpg'
                    thumbnail_content = ContentFile(thumbnail_io.getvalue(), thumbnail_filename)
                    
                    video.thumbnail.save(thumbnail_filename, thumbnail_content)
                    
                    # Print video duration for debugging
                    print(f"Video length: {video_duration} seconds")
                    
                except Exception as e:
                    form.add_error(None, f"Error processing video: {str(e)}")
            video.save()
            return redirect('video_list')
    else:
        form = VideoForm()
    
    return render(request, 'upload_video.html', {'form': form})


def video_list(request):
    """
    Displays the list of uploaded videos with their timestamps.
    """
    videos = Video.objects.all().order_by('-id')

    # Generate a list of tuples which have videos and images, where timestamp is extracted from the filename
    video_data = []
    for video in videos:
        if video.thumbnail:
            # Extract timestamp from the filename if available
            filename = video.thumbnail.name
            if filename:
                try:
                    # Extract timestamp from the filename
                    parts = filename.split('_')
                    timestamp_str = parts[-1].replace('.jpg', '')
                    timestamp = float(timestamp_str)
                except (ValueError, IndexError):
                    timestamp = None
            else:
                timestamp = None
        else:
            timestamp = None
        video_data.append((video, timestamp))
    
    return render(request, 'video_list.html', {'video_data': video_data})
