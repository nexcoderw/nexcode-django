from django import forms
from home.models import *

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Your Name', 'required': 'true'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Your Email', 'required': 'true'}),
            'subject': forms.TextInput(attrs={'placeholder': 'Subject', 'required': 'true'}),
            'message': forms.Textarea(attrs={'placeholder': 'Your Message', 'rows': 4, 'required': 'true'}),
        }

class TestimonyForm(forms.Form):
    name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'placeholder': 'Your Name', 'required': 'true'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'Your Email', 'required': 'true'})
    )
    phone_number = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'placeholder': 'Your Phone Number', 'required': 'true'})
    )
    image = forms.ImageField(required=False)
    message = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Your Testimony', 'rows': 4, 'required': 'true'})
    )