
from django import forms
from home.models import *
from taggit.forms import TagWidget
from django.core.validators import RegexValidator

_phone_validator = RegexValidator(
    r"^\+?[0-9]{9,15}$",
    "Enter a valid phone number (9–15 digits, optional leading ‘+’)."
)

class ClientForm(forms.ModelForm):
    """Professional form for creating a Client with strong validation."""

    phone_number = forms.CharField(
        required=True,
        validators=[_phone_validator],
        widget=forms.TextInput(attrs={
            "placeholder": "Client Phone Number",
            "class": ("h-10 w-full rounded-md border bg-background px-3 py-2 ring-offset-background file:border-0 file:bg-transparent file:font-medium file:text-foreground placeholder:text-foreground/70 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-foreground/5 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 "
                      "focus-visible:outline-none focus-visible:ring-2 "
                      "focus-visible:ring-foreground/5 focus-visible:ring-offset-2")
        })
    )

    class Meta:
        model  = Client
        fields = ("name", "email", "phone_number", "image")
        widgets = {
            "name": forms.TextInput(attrs={
                "placeholder": "Client Name",
                "class": ("h-10 w-full rounded-md border bg-background px-3 py-2 ring-offset-background file:border-0 file:bg-transparent file:font-medium file:text-foreground placeholder:text-foreground/70 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-foreground/5 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 "
                          "focus-visible:outline-none focus-visible:ring-2 "
                          "focus-visible:ring-foreground/5 focus-visible:ring-offset-2")
            }),
            "email": forms.EmailInput(attrs={
                "placeholder": "Client Email",
                "class": ("h-10 w-full rounded-md border bg-background px-3 py-2 ring-offset-background file:border-0 file:bg-transparent file:font-medium file:text-foreground placeholder:text-foreground/70 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-foreground/5 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 "
                          "focus-visible:outline-none focus-visible:ring-2 "
                          "focus-visible:ring-foreground/5 focus-visible:ring-offset-2")
            }),
        }

    def clean_email(self):
        email = self.cleaned_data["email"]
        qs = Client.objects.filter(email__iexact=email)

        # ✨  Ignore the record we’re currently editing
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise forms.ValidationError("A client with this email already exists.")
        return email

class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ('name', 'position', 'image', 'image_png', 'linkedin', 'github')
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Full Name',
                "class": ("h-10 w-full rounded-md border bg-background px-3 py-2 ring-offset-background file:border-0 file:bg-transparent file:font-medium file:text-foreground placeholder:text-foreground/70 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-foreground/5 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 "
                          "focus-visible:outline-none focus-visible:ring-2 "
                          "focus-visible:ring-foreground/5 focus-visible:ring-offset-2")
            }),
            'position': forms.TextInput(attrs={
                'placeholder': 'Position/Role',
                "class": ("h-10 w-full rounded-md border bg-background px-3 py-2 ring-offset-background file:border-0 file:bg-transparent file:font-medium file:text-foreground placeholder:text-foreground/70 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-foreground/5 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 "
                          "focus-visible:outline-none focus-visible:ring-2 "
                          "focus-visible:ring-foreground/5 focus-visible:ring-offset-2")
            }),
            'linkedin': forms.URLInput(attrs={
                'placeholder': 'LinkedIn Profile URL',
                "class": ("h-10 w-full rounded-md border bg-background px-3 py-2 ring-offset-background file:border-0 file:bg-transparent file:font-medium file:text-foreground placeholder:text-foreground/70 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-foreground/5 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 "
                          "focus-visible:outline-none focus-visible:ring-2 "
                          "focus-visible:ring-foreground/5 focus-visible:ring-offset-2")
            }),
            'github': forms.URLInput(attrs={
                'placeholder': 'GitHub Profile URL',
                "class": ("h-10 w-full rounded-md border bg-background px-3 py-2 ring-offset-background file:border-0 file:bg-transparent file:font-medium file:text-foreground placeholder:text-foreground/70 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-foreground/5 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 "
                          "focus-visible:outline-none focus-visible:ring-2 "
                          "focus-visible:ring-foreground/5 focus-visible:ring-offset-2")
            }),
        }

_input_class = ("h-10 w-full rounded-md border bg-background px-3 py-2 ring-offset-background file:border-0 file:bg-transparent file:font-medium file:text-foreground placeholder:text-foreground/70 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-foreground/5 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 "
                          "focus-visible:outline-none focus-visible:ring-2 "
                          "focus-visible:ring-foreground/5 focus-visible:ring-offset-2")

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
            'name': forms.TextInput(attrs={'class': _input_class, 'placeholder': 'Project Name'}),
            'link': forms.TextInput(attrs={'class': _input_class, 'placeholder': 'Project Link'}),
            'image': forms.ClearableFileInput(attrs={'class': _input_class}),
            'big_image': forms.ClearableFileInput(attrs={'class': _input_class}),
            'category': forms.Select(attrs={'class': _input_class}),
            'description': forms.Textarea(attrs={'class': _input_class, 'rows': 4, 'placeholder': 'Project Description'}),
            'tags': TagWidget(attrs={'class': _input_class}),
            'repo_link': forms.URLInput(attrs={'class': _input_class, 'placeholder': 'Repository Link'}),
            'figma_link': forms.URLInput(attrs={'class': _input_class, 'placeholder': 'Figma Link'}),
            'project_category': forms.Select(attrs={'class': _input_class}),
            'system_analysis_document': forms.ClearableFileInput(attrs={'class': _input_class}),
            'publish': forms.CheckboxInput(attrs={'class': ''}),  # checkbox styling typically differs
            'client': forms.Select(attrs={'class': _input_class}),
            'team_members': forms.SelectMultiple(attrs={'class': _input_class}),
            'contract_document': forms.ClearableFileInput(attrs={'class': _input_class}),
            'project_initiation_date': forms.DateInput(attrs={'class': _input_class, 'type': 'date'}),
            'deadline_date': forms.DateInput(attrs={'class': _input_class, 'type': 'date'}),
            'project_amount': forms.NumberInput(attrs={'class': _input_class, 'placeholder': 'Project Amount'}),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise forms.ValidationError("Project name is required.")
        return name

class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ['title', 'featured_image', 'content', 'excerpt', 'tags', 'category', 'status']
        widgets = {
            'title': forms.TextInput(attrs={'class': _input_class, 'placeholder': 'Blog Title'}),
            'featured_image': forms.ClearableFileInput(attrs={'class': _input_class}),
            'content': forms.Textarea(attrs={'class': _input_class, 'rows': 6, 'placeholder': 'Write your blog content here...'}),
            'excerpt': forms.Textarea(attrs={'class': _input_class, 'rows': 3, 'placeholder': 'Brief excerpt or summary'}),
            'tags': TagWidget(attrs={'class': _input_class}),
            'category': forms.TextInput(attrs={'class': _input_class, 'placeholder': 'Category'}),
            'status': forms.Select(attrs={'class': _input_class}),
        }

class TestimonyForm(forms.ModelForm):
    class Meta:
        model = Testimony
        fields = ['client', 'message']
        widgets = {
            'client': forms.Select(attrs={'class': _input_class}),
            'message': forms.Textarea(attrs={'class': _input_class, 'rows': 5, 'placeholder': 'Enter testimony message'}),
        }

class TrainingForm(forms.ModelForm):
    class Meta:
        model = Training
        fields = ['title', 'image', 'description', 'price', 'start_date', 'end_date', 'status']
        widgets = {
            'title': forms.TextInput(attrs={'class': _input_class, 'placeholder': 'Training Title'}),
            'image': forms.ClearableFileInput(attrs={'class': _input_class}),
            'description': forms.Textarea(attrs={'class': _input_class, 'rows': 5, 'placeholder': 'Describe the training'}),
            'price': forms.NumberInput(attrs={'class': _input_class, 'placeholder': 'Price'}),
            'start_date': forms.DateInput(attrs={'class': _input_class, 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': _input_class, 'type': 'date'}),
            'status': forms.Select(attrs={'class': _input_class}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("start_date")
        end = cleaned_data.get("end_date")

        if start and end and end < start:
            raise forms.ValidationError("End date cannot be earlier than start date.")

        return cleaned_data