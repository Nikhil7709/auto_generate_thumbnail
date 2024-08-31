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
    Captures screenshots from the provided video file.
    Returns two BytesIO objects: one for the 2:1 aspect ratio thumbnail and another for the 300x140 thumbnail.
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
                screenshot_time = duration / 2
            else:
                screenshot_time = round(timestamp)
        else:
            screenshot_time = duration / 2

        screenshot_time = min(max(screenshot_time, 0), duration - 1)

        # Capture the frame at the determined screenshot_time
        screenshot = clip.get_frame(screenshot_time)

        # Convert screenshot to PIL Image
        screenshot_image = Image.fromarray(screenshot)

        # Target dimensions for the thumbnails
        target_size_300x140 = (300, 140)
        target_aspect_ratio = (2, 1)

        # Generate the 300x140 thumbnail with 'cover' effect
        thumbnail_300x140 = crop_center_with_cover_effect(screenshot_image, *target_size_300x140)

        # Generate the 2:1 aspect ratio thumbnail with 'cover' effect
        thumbnail_2x1 = crop_center_with_aspect_ratio(screenshot_image, target_aspect_ratio)

        # Convert the images to BytesIO
        thumbnail_io_300x140 = BytesIO()
        thumbnail_300x140.save(thumbnail_io_300x140, format='PNG', quality=100)

        thumbnail_io_2x1 = BytesIO()
        thumbnail_2x1.save(thumbnail_io_2x1, format='PNG', quality=100)

        thumbnail_io_300x140.seek(0)
        thumbnail_io_2x1.seek(0)

        return thumbnail_io_300x140, thumbnail_io_2x1, duration, screenshot_time


def crop_center_with_cover_effect(image, width, height):
    """
    Crop the center of the image to cover the specified width and height.
    """
    img_width, img_height = image.size

    target_aspect_ratio = width / height
    img_aspect_ratio = img_width / img_height

    if img_aspect_ratio > target_aspect_ratio:
        new_height = height
        new_width = int(img_aspect_ratio * new_height)
    else:
        new_width = width
        new_height = int(new_width / img_aspect_ratio)

    # Resize image to new dimensions maintaining aspect ratio
    resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Calculate the center crop box
    left = (new_width - width) // 2
    top = (new_height - height) // 2
    right = left + width
    bottom = top + height

    # Crop to the target size
    cropped_image = resized_image.crop((left, top, right, bottom))

    return cropped_image


def crop_center_with_aspect_ratio(image, aspect_ratio):
    """
    Crop the image to the specified aspect ratio from the center with 'cover' effect.
    """
    aspect_ratio_width, aspect_ratio_height = aspect_ratio
    img_width, img_height = image.size

    img_aspect_ratio = img_width / img_height
    target_aspect_ratio = aspect_ratio_width / aspect_ratio_height

    if img_aspect_ratio > target_aspect_ratio:
        new_height = img_height
        new_width = int(target_aspect_ratio * new_height)
    else:
        new_width = img_width
        new_height = int(new_width / target_aspect_ratio)

    left = (img_width - new_width) // 2
    top = (img_height - new_height) // 2
    right = left + new_width
    bottom = top + new_height

    # Crop and resize image to fit the aspect ratio
    cropped_image = image.crop((left, top, right, bottom))

    return cropped_image

