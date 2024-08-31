import os
from django.http import HttpResponseBadRequest
from django.shortcuts import render, redirect
from .forms import VideoForm
from .models import Video
from .utils import capture_screenshot, download_video, get_video_file

from django.core.files.base import ContentFile
from django.conf import settings
import io


def upload_video(request):
    """
    Handles video upload from a URL or local file path and thumbnail generation.
    """
    if request.method == 'POST':
        form = VideoForm(request.POST)
        video_path = request.POST.get('video_path', None)
        timestamp_str = request.POST.get('timestamp', None)
        timestamp = None
        
        if timestamp_str:
            try:
                timestamp = float(timestamp_str)
            except ValueError:
                return HttpResponseBadRequest("Invalid timestamp format.")
        
        if video_path:
            # Determine if the path is a URL or local file path
            if video_path.startswith('http://') or video_path.startswith('https://'):
                video_file = download_video(video_path)
            else:
                try:
                    with open(video_path, 'rb') as f:
                        video_file = io.BytesIO(f.read())
                except FileNotFoundError:
                    return HttpResponseBadRequest("Local file not found.")
            if video_file:
                try:
                    # Capture and resize the screenshot and get the video duration
                    thumbnail_io, video_duration, screenshot_time = capture_screenshot(video_file, timestamp)
                    
                    # Format filename with timestamp if available
                    thumbnail_filename = f'thumbnail_{screenshot_time:.2f}.png'
                    thumbnail_content = ContentFile(thumbnail_io.getvalue(), thumbnail_filename)
                    
                    # Save the thumbnail
                    video = Video(video_url=video_path)
                    video.thumbnail.save(thumbnail_filename, thumbnail_content)
                    video.save()
                    
                    # Print video duration for debugging
                    print(f"Video length: {video_duration} seconds")
                    
                except Exception as e:
                    return HttpResponseBadRequest(f"Error processing video: {str(e)}")
            else:
                return HttpResponseBadRequest("Error downloading or accessing the video.")
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
