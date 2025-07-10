from django import forms
from .models import Project, Task, TaskSubmission, ProjectComment
from django.contrib.auth import get_user_model

User = get_user_model()

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'repository_url', 'category', 'image_url']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'category': forms.Select(choices=Project._meta.get_field('category').choices),
            'image_url': forms.URLInput(attrs={'placeholder': 'https://example.com/image.jpg'}),
        }
    def clean_image_url(self):
        image_url = self.cleaned_data.get('image_url')
        if image_url:
            # تحقق اختياري: التأكد من أن الرابط ينتهي بامتداد صورة
            valid_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp')
            if not any(image_url.lower().endswith(ext) for ext in valid_extensions):
                raise forms.ValidationError('Please enter a valid image URL (e.g., ending with .jpg, .png, .gif).')
        return image_url

class TaskForm(forms.ModelForm):
    assigned_to = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(courses_profile__role='student'),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )
    class Meta:
        model = Task
        fields = ['title', 'description', 'issue_url', 'priority', 'xp_reward', 'coins_reward', 'due_date', 'assigned_to']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'priority': forms.Select(choices=Task.PRIORITY_CHOICES),
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class TaskSubmissionForm(forms.ModelForm):
    class Meta:
        model = TaskSubmission
        fields = ['submission_url', 'file_url', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'file_url': forms.URLInput(attrs={'placeholder': 'https://example.com/file'}),
        }

class ProjectCommentForm(forms.ModelForm):
    class Meta:
        model = ProjectComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3}),
        }
        
from django import forms
from .models import SubmissionComment, SubmissionRating

class SubmissionCommentForm(forms.ModelForm):
    class Meta:
        model = SubmissionComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

class SubmissionRatingForm(forms.ModelForm):
    class Meta:
        model = SubmissionRating
        fields = ['rating']
        widgets = {
            'rating': forms.Select(choices=[(i, str(i)) for i in range(1, 6)], attrs={'class': 'form-control'}),
        }
        
from django import forms
from .models import CollaborationRoom, RoomMessage, RoomFile, RoomTask

class RoomForm(forms.ModelForm):
    class Meta:
        model = CollaborationRoom
        fields = ['title', 'project', 'task']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'project': forms.Select(attrs={'class': 'form-control'}),
            'task': forms.Select(attrs={'class': 'form-control'}),
        }

class MessageForm(forms.ModelForm):
    class Meta:
        model = RoomMessage
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class FileForm(forms.ModelForm):
    class Meta:
        model = RoomFile
        fields = ['file']
        widgets = {
            'file': forms.FileInput(attrs={'class': 'form-control'}),
        }

class RoomTaskForm(forms.ModelForm):
    class Meta:
        model = RoomTask
        fields = ['title', 'description', 'assigned_to', 'status']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'assigned_to': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }