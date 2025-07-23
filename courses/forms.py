from django import forms
from .models import Course, Video, Task, AlternativeQuiz
import json

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'category', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'category': forms.Select(choices=Course.CATEGORY_CHOICES),
            'image': forms.URLInput(attrs={'placeholder': 'Enter image URL (e.g., Google Drive link)'}),
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
            if not image_url.startswith(('http://', 'https://')):
                raise forms.ValidationError("Please enter a valid URL starting with http:// or https://")
        return image_url

class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['title', 'video_url', 'description', 'order']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Enter video title'}),
            'description': forms.Textarea(attrs={'placeholder': 'Enter video description'}),
            'video_url': forms.URLInput(attrs={'placeholder': 'Enter video URL (e.g., Google Drive link)'}),
            'order': forms.NumberInput(attrs={'placeholder': 'Enter video order'}),
        }
        labels = {
            'title': 'Video Title',
            'description': 'Description',
            'video_url': 'Video URL',
            'order': 'Order',
        }

    def clean(self):
        cleaned_data = super().clean()
        video_url = cleaned_data.get('video_url')
        if not video_url:
            raise forms.ValidationError("يجب إدخال رابط فيديو.")
        return cleaned_data

class TaskForm(forms.ModelForm):
    questions_json = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5, 'placeholder': 'Enter questions as JSON'}),
        required=True,
        label="Questions (JSON format)"
    )

    class Meta:
        model = Task
        fields = ['title', 'order', 'questions_json']

    def clean_questions_json(self):
        data = self.cleaned_data['questions_json']
        try:
            questions = json.loads(data)
            if not isinstance(questions, list):
                raise forms.ValidationError("Questions must be a JSON list.")
            for q in questions:
                if not all(key in q for key in ['question', 'options', 'correct_answer']):
                    raise forms.ValidationError("Each question must have 'question', 'options', and 'correct_answer'.")
                if not isinstance(q['options'], list):
                    raise forms.ValidationError("'options' must be a list.")
        except json.JSONDecodeError:
            raise forms.ValidationError("Invalid JSON format.")
        return questions

class AlternativeQuizForm(forms.ModelForm):
    class Meta:
        model = AlternativeQuiz
        fields = ['question', 'options', 'correct_answer']
        widgets = {
            'question': forms.Textarea(attrs={'rows': 3}),
            'options': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter options as JSON list, e.g., ["option1", "option2", "option3"]'}),
        }

    def clean_options(self):
        options = self.cleaned_data['options']
        if isinstance(options, str):
            try:
                options = json.loads(options)
                if not isinstance(options, list):
                    raise forms.ValidationError("Options must be a JSON list.")
            except json.JSONDecodeError:
                raise forms.ValidationError("Invalid JSON format for options.")
        return options