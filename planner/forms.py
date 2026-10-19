"""Forms for authentication, tasks, exams, and study sessions."""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Task, Exam, StudySession
from django.utils import timezone


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label='Email',
        widget=forms.EmailInput(attrs={'placeholder': 'you@example.com', 'class': 'form-input'}),
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Choose a username', 'class': 'form-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-input', 'placeholder': 'Create a password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-input', 'placeholder': 'Confirm your password'})
        self.fields['username'].help_text = ''

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'subject', 'due_date', 'priority']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input', 'placeholder': 'e.g. Complete Python assignment / Lab record',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-input', 'rows': 3,
                'placeholder': 'Optional – details, submission instructions, requirements, etc.',
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-input', 'placeholder': 'e.g. Python, Operating Systems, Web Dev, Project',
            }),
            'due_date': forms.DateInput(attrs={
                'class': 'form-input', 'type': 'date',
            }),
            'priority': forms.Select(attrs={'class': 'form-input form-select'}),
        }

    def clean_due_date(self):
        due_date = self.cleaned_data.get('due_date')
        # Allow past dates for editing existing tasks – no restriction
        return due_date


class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ['name', 'subject', 'exam_date', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input', 'placeholder': 'e.g. Lab Exam, Semester Exam, Midterm',
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-input', 'placeholder': 'e.g. Python Programming, Operating Systems, DBMS',
            }),
            'exam_date': forms.DateInput(attrs={
                'class': 'form-input', 'type': 'date',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-input', 'rows': 3,
                'placeholder': 'Optional – syllabus units, lab experiments, topics to revise',
            }),
        }


class StudySessionForm(forms.ModelForm):
    start_time = forms.TimeField(
        input_formats=['%H:%M', '%H:%M:%S', '%I:%M %p', '%I:%M%p', '%I:%M:%S %p'],
        widget=forms.TimeInput(attrs={
            'class': 'form-input', 'type': 'time',
        }),
    )

    class Meta:
        model = StudySession
        fields = ['subject', 'study_date', 'start_time', 'duration_minutes']
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'form-input', 'placeholder': 'e.g. Python OOPs & Django, Operating Systems, Project Work',
            }),
            'study_date': forms.DateInput(attrs={
                'class': 'form-input', 'type': 'date',
            }),
            'duration_minutes': forms.NumberInput(attrs={
                'class': 'form-input', 'placeholder': '60', 'min': '5', 'max': '480',
            }),
        }
        labels = {
            'duration_minutes': 'Duration (minutes)',
        }
