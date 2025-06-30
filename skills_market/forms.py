from django import forms
from .models import Skill, Service, ServiceOrder, Opportunity

class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ['name', 'description', 'level']

class ServiceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['skill'].queryset = Skill.objects.filter(user=user)

    class Meta:
        model = Service
        fields = ['skill', 'title', 'description', 'price_coins', 'delivery_time_days']

class ServiceOrderForm(forms.ModelForm):
    class Meta:
        model = ServiceOrder
        fields = []  # No fields needed for now

        
from django import forms
from .models import OpportunityApplication, Opportunity

class OpportunityApplicationForm(forms.ModelForm):
    class Meta:
        model = OpportunityApplication
        fields = ['full_name', 'phone_number', 'address', 'age', 'skills', 'experience', 'cv', 'linkedin','github', 'email']

class OpportunityForm(forms.ModelForm):
    class Meta:
        model = Opportunity
        fields = ['title', 'description', 'salary', 'address', 'required_skills', 'email']
        widgets = {
            'required_skills': forms.CheckboxSelectMultiple(),
        }
from django import forms

class OrderForm(forms.Form):
    details = forms.CharField(
        widget=forms.Textarea,
        label="Order Details",
        help_text="Provide any specific instructions for the service.",
        required=True
    )

from django import forms
from .models import Message

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content', 'file']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3}),
        }
        
        
