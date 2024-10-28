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