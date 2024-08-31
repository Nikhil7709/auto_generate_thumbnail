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
    If a timestamp is provided and valid, captures the frame at that specific time (rounded to whole seconds).
    If the timestamp is invalid or not provided, captures a random screenshot (rounded to whole seconds).
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
                # Invalid timestamp, fallback to random screenshot
                screenshot_time = round(random.uniform(0, duration))
            else:
                # Round timestamp to nearest whole second
                screenshot_time = round(timestamp)
        else:
            screenshot_time = round(random.uniform(0, duration))
        
        # Ensure screenshot_time is within the video duration
        screenshot_time = min(max(screenshot_time, 0), duration - 1)
        
        # Capture the frame at the determined screenshot_time
        screenshot = clip.get_frame(screenshot_time)

        # Convert screenshot to PIL Image
        screenshot_image = Image.fromarray(screenshot)
        
        # Target dimensions
        target_width, target_height = 300, 140
        
        # Calculate the aspect ratio
        aspect_ratio = target_width / target_height
        
        # Get original dimensions
        original_width, original_height = screenshot_image.size
        print("at line 67", original_width, original_height)
        # Determine crop box to fit the aspect ratio
        if original_width / original_height > aspect_ratio:
            # Wider than target aspect ratio
            new_width = int(original_height * aspect_ratio)
            new_height = original_height
            left = (original_width - new_width) // 2
            top = 0
            right = left + new_width
            bottom = top + new_height
        else:
            # Taller than target aspect ratio
            new_width = original_width
            new_height = int(original_width / aspect_ratio)
            left = 0
            top = (original_height - new_height) // 2
            right = left + new_width
            bottom = top + new_height
        
        # Crop to fit the target aspect ratio
        cropped_image = screenshot_image.crop((left, top, right, bottom))
        
        # Resize cropped image to 300x140 pixels
        thumbnail_image = cropped_image.resize((target_width, target_height), Image.Resampling.LANCZOS)
    
    # Convert the resized image to bytes with high quality
    thumbnail_io = BytesIO()
    thumbnail_image.save(thumbnail_io, format='PNG', quality=100)
    
    # Reset the file pointer to the beginning
    thumbnail_io.seek(0)
    
    return thumbnail_io, duration, screenshot_time


# def capture_screenshot(video_file, timestamp=None):
#     """
#     Captures a screenshot from the provided video file.
#     If a timestamp is provided, captures the frame at that specific time.
#     If no timestamp is provided, captures a random screenshot.
#     Resizes the screenshot to a thumbnail size with a 2:1 aspect ratio and returns it as BytesIO and the video duration.
#     """
#     with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_video_file:
#         temp_video_file.write(video_file.read())
#         temp_video_file.flush()
        
#         # Load the video clip
#         clip = VideoFileClip(temp_video_file.name)
        
#         # Get the exact duration of the video
#         duration = clip.duration
#         if duration == 0:
#             raise ValueError("Video duration is zero or could not be determined.")
        
#         # Determine the time frame for the screenshot
#         if timestamp is not None:
#             if timestamp < 0 or timestamp > duration:
#                 # Invalid timestamp, fallback to random screenshot
#                 screenshot_time = random.uniform(0, duration)
#             else:
#                 screenshot_time = timestamp
#         else:
#             screenshot_time = random.uniform(0, duration)
        
#         screenshot = clip.get_frame(screenshot_time)

#         # Convert screenshot to PIL Image
#         screenshot_image = Image.fromarray(screenshot)
        
#         # Save the image to BytesIO in high quality
#         original_image_io = BytesIO()
#         screenshot_image.save(original_image_io, format='PNG', quality=100)
#         original_image_io.seek(0)
    
#     # Convert the original image to a thumbnail with a 2:1 aspect ratio
#     original_image = Image.open(original_image_io)
    
#     # Calculate dimensions while maintaining 2:1 aspect ratio
#     width, height = original_image.size
#     aspect_ratio = 2 / 1
    
#     # Determine new size keeping aspect ratio
#     if width / height > aspect_ratio:
#         new_width = int(height * aspect_ratio)
#         new_height = height
#     else:
#         new_width = width
#         new_height = int(width / aspect_ratio)
    
#     # Resize using a high-quality resampling filter
#     thumbnail_image = original_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
#     # Convert the resized image to bytes with high quality
#     thumbnail_io = BytesIO()
#     thumbnail_image.save(thumbnail_io, format='PNG', quality=100)  # Save as PNG to retain quality
    
#     # Reset the file pointer to the beginning
#     thumbnail_io.seek(0)
    
#     return thumbnail_io, duration, screenshot_time
