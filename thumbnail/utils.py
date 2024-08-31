import requests
import tempfile
import os
from moviepy.editor import VideoFileClip
from io import BytesIO
from PIL import Image


def get_video_file(video_path):
    """
    Fetches the video from a URL or local file path.
    Returns a BytesIO object of the video if successful, else returns None
    """
    if video_path.startswith(('http://', 'https://')):
        # Handle URL
        response = requests.get(video_path, stream=True)
        if response.status_code == 200:
            return BytesIO(response.content)
        return None
    else:
        # Handle local file path
        if os.path.exists(video_path):
            with open(video_path, 'rb') as f:
                return BytesIO(f.read())
        return None


def download_video(video_url):
    """
    Downloads the video from the provided URL.
    Returns a BytesIO object of the video if successful, else returns None
    """
    response = requests.get(video_url, stream=True)
    if response.status_code == 200:
        return BytesIO(response.content)
    return None

def capture_screenshot(video_file, timestamp=None):
    """
    Captures a screenshot from the provided video file.
    If a timestamp is provided and valid, captures the frame at that specific time rounded to whole seconds.
    If the timestamp is invalid or not provided, captures a screenshot from the center of a random frame.
    Crops a centered 300x140 pixels thumbnail from the video and returns it as BytesIO and the video duration.
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
                # Invalid timestamp, fallback to center of random frame
                screenshot_time = duration / 2
            else:
                # Round timestamp to nearest whole second
                screenshot_time = round(timestamp)
        else:
            screenshot_time = duration / 2
        
        # Ensure screenshot_time is within the video duration
        screenshot_time = min(max(screenshot_time, 0), duration - 1)
        
        # Capture the frame at the determined screenshot_time
        screenshot = clip.get_frame(screenshot_time)

        # Convert screenshot to PIL Image
        screenshot_image = Image.fromarray(screenshot)
        
        # Target dimensions
        target_width, target_height = 300, 140
        
        # Get original dimensions
        original_width, original_height = screenshot_image.size
        
        # Calculate crop box centered around the center of the image
        center_x, center_y = original_width // 2, original_height // 2
        crop_width = min(original_width, target_width)
        crop_height = min(original_height, target_height)
        
        left = max(center_x - crop_width // 2, 0)
        top = max(center_y - crop_height // 2, 0)
        right = min(center_x + crop_width // 2, original_width)
        bottom = min(center_y + crop_height // 2, original_height)
        
        # Crop to fit the target aspect ratio centered around the center
        cropped_image = screenshot_image.crop((left, top, right, bottom))
        
        # Resize cropped image to 300x140 pixels
        thumbnail_image = cropped_image.resize((target_width, target_height), Image.Resampling.LANCZOS)
    
    # Convert the resized image to bytes with high quality
    thumbnail_io = BytesIO()
    thumbnail_image.save(thumbnail_io, format='PNG', quality=100)
    
    # Reset the file pointer to the beginning
    thumbnail_io.seek(0)
    
    return thumbnail_io, duration, screenshot_time

