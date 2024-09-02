from django import forms
from .models import Video

# class VideoForm(forms.ModelForm):
#     video_path = forms.CharField(label='Video URL or Local Path', widget=forms.TextInput(attrs={'placeholder': 'Enter URL or local path'}))
    
#     class Meta:
#         model = Video
#         fields = ['video_path']


class VideoForm(forms.ModelForm):
    video_path = forms.CharField(
        label='Video URL or Local Path',
        widget=forms.TextInput(attrs={'placeholder': 'Enter URL or local path'})
    )
    aspect_ratio = forms.CharField(
        label='Aspect Ratio (width:height, optional)',
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'e.g., 2:1'})
    )

    class Meta:
        model = Video
        fields = ['video_path', 'aspect_ratio']