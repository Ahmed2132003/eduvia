from django import forms
from .models import Competition

from django import forms
from .models import Competition
from django.utils.text import slugify
import re

def clean_text(text):
    if not text or not text.strip():
        return 'default-title'
    text = re.sub(r'[^\w\s\-\u0600-\u06FF]', '', str(text)).strip()
    cleaned = text if text else 'default-title'
    slugified = slugify(cleaned, allow_unicode=True)
    return slugified if slugified else 'default-title'
class CompetitionForm(forms.ModelForm):
    class Meta:
        model = Competition
        fields = ['title', 'description', 'start_time', 'end_time', 'question_time_limit']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if not title or not title.strip():
            raise forms.ValidationError("العنوان لا يمكن أن يكون فارغًا.")
        cleaned_title = clean_text(title)
        if cleaned_title == 'default-title':
            raise forms.ValidationError("العنوان يجب أن يحتوي على أحرف صالحة لإنشاء رابط.")
        return title