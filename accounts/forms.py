from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class RegistrationForm(UserCreationForm):
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, widget=forms.RadioSelect)

    class Meta:
        model = User
        fields = ['username', 'email', 'role', 'password1', 'password2']

from django import forms
from .models import Profile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['full_name', 'profile_picture', 'date_of_birth']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'profile_picture': forms.URLInput(attrs={'placeholder': 'Enter image URL (e.g., https://i.postimg.cc/...)'}),
        }
from django import forms
from .models import UserMessage

class MessageForm(forms.ModelForm):
    class Meta:
        model = UserMessage
        fields = ['content', 'file']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3}),
        }