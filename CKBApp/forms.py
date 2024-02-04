# CKBApp/forms.py
from django import forms
from .models import User, Student, Educator, Tournament

class RegistrationForm(forms.Form):
    name = forms.CharField(max_length=100)
    surname = forms.CharField(max_length=100)
    email = forms.EmailField(required=False)
    password = forms.CharField(max_length=100, widget=forms.PasswordInput(render_value=True))
    user_type = forms.ChoiceField(choices=[('student', 'Student'), ('educator', 'Educator')])
    github_username = forms.CharField(max_length=100)


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


class TournamentCreationForm (forms.Form):
    name= forms.CharField(max_length=100, required=True)
    description = forms.CharField(widget=forms.Textarea)
    submission_deadline = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)
    ending_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)





class PermissionForm(forms.Form):
    educator_granted = forms.CharField(label="Enter educator's name", max_length=100)


class TeamRegistrationForm(forms.Form):
    team_name = forms.CharField(label="Enter team's name", max_length=100)

class InvitationForm(forms.Form):
    mate_email = forms.CharField(label="Enter teammate's name", max_length=100)