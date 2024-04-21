from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django import forms
from .models import User, Carrito
from django import forms
from django.contrib.auth.hashers import check_password
from datetime import date

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

# Forms para Filtros/Carrito
class DateInput(forms.DateInput):
     input_type = 'date'

class FiltrosForm(forms.ModelForm):
    """
    Form para filtrar catalogo/carrito
    """

    # TODO: Cambiar plantilla Filtros a widgets

    class Meta:
        model = Carrito
        fields = ['inicio', 'materia', 'final']
        widgets = {
            'inicio': DateInput,
        }