from .models import User,Message
from django.contrib.auth.forms import UserCreationForm
from django import forms


class UserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username','email','phone_number','password1','password2']
        
        
        
class ContactForm(forms.Form):
    phone_number = forms.CharField(max_length=11, required=False)
    email = forms.EmailField(required=False)
    
    
class MessageForm(forms.ModelForm):
    """Form definition for MODELNAME."""
    text = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Type a message...',
            'autocomplete': 'off'
        }),
        required=False
    )

    class Meta:
        """Meta definition for MODELNAMEform."""

        model = Message
        fields = ['text']


class ImageForm(forms.ModelForm):
    """Form definition for MODELNAME."""

    class Meta:
        """Meta definition for MODELNAMEform."""

        model = Message
        fields = ['image']

    