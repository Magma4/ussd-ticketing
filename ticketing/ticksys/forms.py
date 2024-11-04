from typing import Any
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import *

# class Login(forms.ModelForm):
#     class Meta:
#         model = User
#         fields = ['username',  'password']

class Register(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({
            'required': '',
            'name': 'username',
            'id': 'username',
            'type': 'text',
            'class': 'form-control',
            'placeholder': 'username',
            'aria-label': 'username',
            'minlength': '4'
        })
        self.fields["first_name"].widget.attrs.update({
            'required': '',
            'name': 'first_name',
            'id': 'first_name',
            'type': 'text',
            'class': 'col form-control',
            'placeholder': 'Firstname',
            'aria-label': 'first_name'
        })
        self.fields["last_name"].widget.attrs.update({
            'required': '',
            'name': 'last_name',
            'id': 'last_name',
            'type': 'text',
            'class': 'col form-control',
            'placeholder': 'Lastname',
            'aria-label': 'last_name'
        })
        self.fields["email"].widget.attrs.update({
            'required': '',
            'name': 'email',
            'id': 'email',
            'type': 'email',
            'class': 'form-control',
            'placeholder': 'Email',
            'aria-label': 'email'
        })
        self.fields["password1"].widget.attrs.update({
            'required': '',
            'name': 'password1',
            'id': 'inputPassword5',
            'type': 'password',
            'class': 'form-control',
            'placeholder': 'Create Password',
            'aria-describedby': 'passwordHelpBlock'
        })
        self.fields["password2"].widget.attrs.update({
            'required': '',
            'name': 'password2',
            'id': 'inputPassword5',
            'type': 'password',
            'class': 'form-control',
            'placeholder': 'Confirm Password',
            'aria-describedby': 'passwordHelpBlock'
        })

    def clean_username(self):
        username = self.cleaned_data['username']
        return username.lower()

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['username'].lower()  # Convert username to lowercase
        if commit:
            user.save()
        return user

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email',  'password1', 'password2' ]


class TicketSearchForm(forms.Form):
    id_number = forms.CharField(label='Enter ID number', max_length=100)

    # forms.py
from django import forms
from .models import Ticket

class TicketForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        # Example: Customize form fields based on request
        if self.request and self.request.user:
            # Customize form fields here based on user or request data
            pass

    class Meta:
        model = Ticket
        fields = ['mode', 'client_type', 'id_number', 'category', 'description']
        widgets = {
            'description': forms.TextInput(attrs={'placeholder': 'Type exact issue here...'}),
        }
