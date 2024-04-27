from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .models import Carrito, Prestatario


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

    materia = forms.ModelChoiceField(queryset=None, required=True, empty_label='--- Selecciona una materia ---')
    duracion = forms.ChoiceField(label="Tiempo", required=True, choices=[
        (1, "1 hora"),
        (2, "2 hora"),
        (3, "3 hora"),
        (4, "4 hora"),
        (8, "8 hora"),
        (24, "1 dia (24h)"),
        (48, "2 dias (48h)"),
        (72, "3 días (72h)"),
        (96, "4 dias (96h)"),
    ])
    hora_inicio = forms.ChoiceField(label="Hora", required=True, choices=[
        ('09:00:00', '9:00 AM'),
        ('09:30:00', '9:30 AM'),
        ('10:00:00', '10:00 AM'),
        ('10:30:00', '10:30 AM'),
        ('11:00:00', '11:00 AM'),
        ('11:30:00', '11:30 AM'),
        ('12:00:00', '12:00 PM'),
        ('12:30:00', '12:30 PM'),
        ('13:00:00', '1:00 PM'),
        ('13:30:00', '1:30 PM'),
        ('14:00:00', '2:00 PM'),
        ('14:30:00', '2:30 PM'),
        ('15:00:00', '3:00 PM'),
        ('15:30:00', '3:30 PM'),
        ('16:00:00', '4:00 PM'),
        ('16:30:00', '4:30 PM'),
        ('17:00:00', '5:00 PM'),
        ('17:30:00', '5:30 PM'),
        ('18:00:00', '6:00 PM'),
        ('18:30:00', '6:30 PM'),
        ('19:00:00', '7:00 PM'),
        ('19:30:00', '7:30 PM'),
        ('20:00:00', '8:00 PM'),
    ])

    def __init__(self, user: Prestatario, *args, **kwargs):
        super(FiltrosForm, self).__init__(*args, **kwargs)
        self.fields['materia'].queryset = user.materias()

    class Meta:
        model = Carrito
        fields = ['inicio', 'materia']
