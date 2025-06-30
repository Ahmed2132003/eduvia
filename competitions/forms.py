from django import forms
from .models import Competition

class CompetitionForm(forms.ModelForm):
    class Meta:
        model = Competition
        fields = ['title', 'description', 'start_time', 'end_time', 'question_time_limit']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }