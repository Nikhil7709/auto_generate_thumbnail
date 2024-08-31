from django import forms
from .models import Video

class VideoForm(forms.ModelForm):
    video_path = forms.CharField(label='Video URL or Local Path', widget=forms.TextInput(attrs={'placeholder': 'Enter URL or local path'}))
    
    class Meta:
        model = Video
        fields = ['video_path']