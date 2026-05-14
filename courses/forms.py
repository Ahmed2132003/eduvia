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
    questions_json = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5, 'placeholder': 'Enter questions as JSON (optional)'}),
        required=False,
        label="Questions for Task (JSON format)"
    )
    task_title = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Enter task title (optional)'})
    )
    task_order = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Enter task order (optional)'})
    )

    class Meta:
        model = Video
        fields = ['title', 'video_url', 'video_file', 'description', 'order', 'duration', 'unlocked']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Enter video title'}),
            'description': forms.Textarea(attrs={'placeholder': 'Enter video description'}),
            'video_url': forms.URLInput(attrs={'placeholder': 'Enter video URL (e.g., Google Drive link)'}),
            'video_file': forms.FileInput(attrs={'placeholder': 'Upload video file (optional)'}),
            'order': forms.NumberInput(attrs={'placeholder': 'Enter video order'}),
            'duration': forms.NumberInput(attrs={'placeholder': 'Enter duration in minutes'}),
            'unlocked': forms.CheckboxInput(),
        }
        labels = {
            'title': 'Video Title',
            'description': 'Description',
            'video_url': 'Video URL',
            'video_file': 'Upload Video',
            'order': 'Order',
            'duration': 'Duration (minutes)',
            'unlocked': 'Unlocked',
        }

    def clean(self):
        cleaned_data = super().clean()
        video_url = cleaned_data.get('video_url')
        video_file = cleaned_data.get('video_file')
        if not video_url and not video_file:
            raise forms.ValidationError("يجب إدخال رابط فيديو أو رفع ملف فيديو.")
        return cleaned_data

    def clean_questions_json(self):
        data = self.cleaned_data['questions_json']
        if data:
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
        return None

class TaskForm(forms.ModelForm):
    video = forms.ModelChoiceField(
        queryset=Video.objects.none(),  # سيتم تعيينه ديناميكيًا
        required=True,
        empty_label="Select a video",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Task
        fields = ['video', 'title', 'order', 'questions']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Enter task title'}),
            'order': forms.NumberInput(attrs={'placeholder': 'e.g. 1, 2, 3...'}),
            'questions': forms.Textarea(attrs={
                'rows': 10,
                'placeholder': '''Example:
[
  {
    "question": "What is Python?",
    "options": ["Language", "Snake", "Tool"],
    "correct_answer": "Language"
  },
  {
    "question": "2 + 2 = ?",
    "options": ["3", "4", "5"],
    "correct_answer": "4"
  }
]'''
            }),
        }

    def __init__(self, *args, course=None, **kwargs):
        super().__init__(*args, **kwargs)
        if course:
            # جيب فيديوهات الكورس بتاع المدرب بس
            self.fields['video'].queryset = course.videos.all().order_by('order')
        else:
            self.fields['video'].queryset = Video.objects.none()

    def clean_questions(self):
        data = self.cleaned_data.get('questions')

        # لو فاضي أو list فاضية
        if not data:
            return []

        # لو جاي list (من initial data مثلاً)
        if isinstance(data, list):
            return data  # نرجعه زي ما هو (لو valid)

        # لو string → ننظفه
        if isinstance(data, str):
            data = data.strip()
            if not data:
                return []

        try:
            questions = json.loads(data)
            if not isinstance(questions, list):
                raise forms.ValidationError("Questions must be a JSON list.")
            for i, q in enumerate(questions):
                if not all(k in q for k in ['question', 'options', 'correct_answer']):
                    raise forms.ValidationError(f"Question {i+1} is missing 'question', 'options', or 'correct_answer'.")
                if not isinstance(q['options'], list):
                    raise forms.ValidationError(f"Options in question {i+1} must be a list.")
            return questions
        except json.JSONDecodeError as e:
            raise forms.ValidationError(f"Invalid JSON: {e}")
        
        
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