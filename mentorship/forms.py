from django import forms
from .models import MentorshipGroup, GroupMessage, MentorRating

class MentorshipGroupForm(forms.ModelForm):
    class Meta:
        model = MentorshipGroup
        fields = ['name', 'description', 'is_public']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'is_public': forms.CheckboxInput(),  # حقل Checkbox لتحديد إذا كان الجروب عام أو خاص
        }
        labels = {
            'name': 'Group Name',
            'description': 'Description',
            'is_public': 'Make this group public (visible to everyone)',
        }
class GroupMessageForm(forms.ModelForm):
    class Meta:
        model = GroupMessage
        fields = ['content', 'file']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
        }

class MentorRatingForm(forms.ModelForm):
    class Meta:
        model = MentorRating
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }