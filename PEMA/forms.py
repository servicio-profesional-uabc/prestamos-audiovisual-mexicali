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

    materia = forms.ChoiceField(label="Materia", required=True)
    final = forms.ChoiceField(label="Tiempo", required=True, choices=[
        (1, "1 hora"),
        (2, "2 hora"),
        (3, "3 hora"),
        (4, "4 hora"),
        (8, "8 hora"),
        (24, "1 dia (24h)"),
        (48, "2 dias (48h)"),
        (96, "4 dias (96h)"),
    ])

    # TODO: Cambiar plantilla Filtros a widgets

    class Meta:
        model = Carrito
        fields = ['inicio', 'materia', 'final']
        widgets = {
            'inicio': forms.DateInput(attrs={'type': 'date'}),
            'final': forms.Select(attrs={'class': 'form-select'}), # fecha_inicio + duracion = fecha_final
        }