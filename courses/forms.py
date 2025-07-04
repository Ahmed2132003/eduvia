from django import forms
from .models import Video
from django.core.exceptions import ValidationError
from django import forms
from .models import Task, AlternativeQuiz
# forms.py
import logging

logger = logging.getLogger(__name__)

class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['title', 'description', 'video_url', 'order', 'unlocked']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Enter video title'}),
            'description': forms.Textarea(attrs={'placeholder': 'Enter video description'}),
            'video_url': forms.URLInput(attrs={'placeholder': 'Enter video URL (e.g., Google Drive link)'}),
            'order': forms.NumberInput(attrs={'placeholder': 'Enter video order'}),
            'unlocked': forms.CheckboxInput(),
        }
        labels = {
            'title': 'Video Title',
            'description': 'Description',
            'video_url': 'Video URL',
            'order': 'Order',
            'unlocked': 'Unlocked',
        }

    def clean(self):
        cleaned_data = super().clean()
        video_url = cleaned_data.get('video_url')

        logger.debug(f"video_url: {video_url}")

        # التحقق من أن رابط الفيديو موجود
        if not video_url:
            raise ValidationError("يجب إدخال رابط فيديو.")
        
        return cleaned_data

class TaskForm(forms.ModelForm):
    questions_json = forms.CharField(widget=forms.Textarea, help_text="Enter questions as JSON array, e.g., [{'question': 'Q1?', 'options': ['A', 'B', 'C'], 'correct_answer': 'A'}, ...]")

    class Meta:
        model = Task
        fields = ['title', 'questions_json', 'order']

    def clean_questions_json(self):
        import json
        questions_json = self.cleaned_data['questions_json']
        try:
            questions = json.loads(questions_json)
            if not isinstance(questions, list):
                raise ValueError("Must be a JSON array")
            for q in questions:
                if not all(k in q for k in ['question', 'options', 'correct_answer']):
                    raise ValueError("Each question must have 'question', 'options', and 'correct_answer'")
            return questions
        except (json.JSONDecodeError, ValueError) as e:
            raise forms.ValidationError(f"Invalid JSON format: {str(e)}")

class AlternativeQuizForm(forms.ModelForm):
    options = forms.CharField(widget=forms.Textarea, help_text="Enter options separated by commas.")

    class Meta:
        model = AlternativeQuiz
        fields = ['question', 'options', 'correct_answer']

    def clean_options(self):
        options = self.cleaned_data['options'].split(',')
        return [option.strip() for option in options if option.strip()]
    
# courses/forms.py
from django import forms
from .models import Course, Video, Task, AlternativeQuiz

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'category', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'category': forms.Select(choices=Course.CATEGORY_CHOICES),
            'image': forms.URLInput(attrs={'placeholder': 'Enter image URL (e.g., Google Drive link)'}),  # تغيير إلى URLInput
        }
        labels = {
            'title': 'Course Title',
            'description': 'Description',
            'category': 'Category',
            'image': 'Image URL',
        }

    def clean_image(self):
        image_url = self.cleaned_data.get('image')
        if image_url:
            # تحقق اختياري: تأكد إن الرابط صالح (مثلًا يبدأ بـ http أو https)
            if not image_url.startswith(('http://', 'https://')):
                raise forms.ValidationError("Please enter a valid URL starting with http:// or https://")
        return image_url
    