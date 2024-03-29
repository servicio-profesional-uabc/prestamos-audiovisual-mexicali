from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import User
# forms.py
from django import forms
from django.contrib.auth.hashers import check_password

class LoginForm(forms.Form):
    """
    Form para login de cualquier usuario User
    """
    matricula = forms.CharField(max_length=9)
    contraseña = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        matricula = cleaned_data.get("matricula")
        password = cleaned_data.get("password")

        if check_password(password, User.objects.get(matricula=matricula, password=password)):
            raise forms.ValidationError("Matrícula y/o contraseña inválidos.")