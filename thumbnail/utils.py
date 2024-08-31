import random
import requests
import tempfile
from moviepy.editor import VideoFileClip
from django.core.files.base import ContentFile
from io import BytesIO
from PIL import Image


def download_video(video_url):
    """
    Downloads the video from the provided URL.
    Returns a BytesIO object of the video if successful, None otherwise.
    """
    response = requests.get(video_url, stream=True)
    if response.status_code == 200:
        return BytesIO(response.content)
    return None



def capture_screenshot(video_file, timestamp=None):
    """
    Captures a screenshot from the provided video file.
    If a timestamp is provided, captures the frame at that specific time.
    If no timestamp is provided, captures a random screenshot.
    Resizes the screenshot to a thumbnail size and returns it as BytesIO and the video duration.
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_video_file:
        temp_video_file.write(video_file.read())
        temp_video_file.flush()
        
        # Load the video clip
        clip = VideoFileClip(temp_video_file.name)
        
        # Get the exact duration of the video
        duration = clip.duration
        if duration == 0:
            raise ValueError("Video duration is zero or could not be determined.")
        
        # Determine the time frame for the screenshot
        if timestamp is not None:
            if timestamp < 0 or timestamp > duration:
                # Invalid timestamp, fallback to random screenshot
                screenshot_time = random.uniform(0, duration)
            else:
                screenshot_time = timestamp
        else:
            screenshot_time = random.uniform(0, duration)
        
        screenshot = clip.get_frame(screenshot_time)

        # Convert screenshot to PIL Image
        screenshot_image = Image.fromarray(screenshot)
        
        # Resize the image to the desired thumbnail size
        thumbnail_image = screenshot_image.resize((300, 140), Image.Resampling.LANCZOS)
    
    # Convert the resized image to bytes
    thumbnail_io = BytesIO()
    thumbnail_image.save(thumbnail_io, format='JPEG')
    
    # Reset the file pointer to the beginning
    thumbnail_io.seek(0)
    
    return thumbnail_io, duration, screenshot_time