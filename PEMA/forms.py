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
    # def __init__(self, *args, **kwargs):
    #     super(FiltrosForm, self).__init__(*args, **kwargs)
    #     current_date = date.today()
    #     if current_date.month <= 6:  # Si es periodo 1
    #         self.fields['inicio'].widget.attrs['min'] = f"{current_date.year}-01-28"
    #         self.fields['inicio'].widget.attrs['max'] = f"{current_date.year}-06-28"
    #     else:  # Second half of the year
    #         self.fields['inicio'].widget.attrs['min'] = f"{current_date.year}-07-01"
    #         self.fields['inicio'].widget.attrs['max'] = f"{current_date.year}-12-31"
    class Meta:
        model = Carrito
        fields = ['inicio']
        widgets = {
            'inicio': DateInput
        }