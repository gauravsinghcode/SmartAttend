from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class StudentSignUpForm(UserCreationForm):
    roll_number = forms.CharField(max_length=50)
    department = forms.CharField(max_length=50)

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'roll_number', 'department', 'password1', 'password2')

    
    def save(self, commit=True):
        user = super().save(commit=True)
        user.role = "student"
        user.roll_number = self.cleaned_data['roll_number']
        user.department = self.cleaned_data['department']
        if commit:
            user.save()
        return user
    

class TeacherSignUpForm(UserCreationForm):
    subject = forms.CharField(max_length=50)
    department = forms.CharField(max_length=50)

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'subject', 'department', 'password1', 'password2')

    
    def save(self, commit=True):
        user = super().save(commit=True)
        user.role = 'teacher'
        user.subject = self.cleaned_data['subject']
        user.department = self.cleaned_data['department']
        if commit:
            user.save()
        return user