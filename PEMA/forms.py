from django.contrib.auth.forms import AuthenticationForm
from django import forms
from .models import Carrito


class UserLoginForm(AuthenticationForm):
    """
    Form para login de cualquier usuario User
    """
    username = forms.CharField()
    password = forms.CharField()


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
