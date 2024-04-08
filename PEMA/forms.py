from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django import forms
from .models import User
from django import forms
from django.contrib.auth.hashers import check_password


class UserLoginForm(AuthenticationForm):
    """
    Form para login de cualquier usuario User
    """
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': '',
            'placeholder': ''
        })
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': '',
            'placeholder': ''
        })
    )
