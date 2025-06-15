from django import forms
from home.models import *
from taggit.forms import TagWidget

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

class PortfolioForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        fields = [
            'name', 'link', 'image', 'big_image', 'category', 'description', 'tags', 'repo_link',
            'figma_link', 'project_category', 'system_analysis_document', 'publish',
            'client', 'team_members', 'contract_document', 'project_initiation_date',
            'deadline_date', 'project_amount'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'project_initiation_date': forms.DateInput(attrs={'type': 'date'}),
            'deadline_date': forms.DateInput(attrs={'type': 'date'}),
            'tags': TagWidget(),
            'team_members': forms.CheckboxSelectMultiple(),
        }
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise forms.ValidationError("Project name is required.")
        return name