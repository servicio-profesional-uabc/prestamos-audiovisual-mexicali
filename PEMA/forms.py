from datetime import date, timedelta, datetime, time

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.core.validators import MaxLengthValidator
from phonenumber_field.formfields import PhoneNumberField

from .models import Carrito, Materia, Perfil, Prestatario


class UpdateUserForm(forms.ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['email']


class ActualizarPerfil(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['numero_telefono']

    numero_telefono = PhoneNumberField(region="MX")


class UserLoginForm(AuthenticationForm):
    """
    Form para login de cualquier usuario User
    """
    username = forms.CharField()
    password = forms.CharField()


# Forms para Filtros/Carrito
class FiltrosForm(forms.ModelForm):
    """
    Form para filtrar catalogo/carrito
    """

    # [x] Agregar fecha inicio agregarle su hora de inicio
    # [x] Sumarle la duracion de horas a dicha fecha
    # [X] Validar que sea elegido en fecha sea 3 dias de anticipacion
    # [X] Validar que inicio sea entre semana (no importa que pase por fin eso se hace extra al hacer solicitud)
    # [X] Guardar dicha fecha final en la variable final de carrito

    class Meta:
        model = Carrito
        fields = ['inicio', 'nombre', 'materia', 'lugar', 'descripcion', 'lugar', 'descripcion_lugar']

    descripcion = forms.CharField(widget=forms.Textarea)

    nombre = forms.CharField(required=True, max_length=250,
                             validators=[MaxLengthValidator(
                                limit_value=250,
                                message='El nombre de la práctica o producción es mayor a 250 caracteres. Intente de nuevo.')]
                            )

    duracion = forms.ChoiceField(required=True, choices=(
        (1, "1 hora"),
        (2, "2 horas"),
        (3, "3 horas"),
        (4, "4 horas"),
        (8, "8 horas"),
        (24, "1 dia (24h)"),
        (48, "2 dias (48h)"),
        (72, "3 días (72h)"),
        (96, "4 dias (96h)"),
    ))

    hora_inicio = forms.ChoiceField(required=True, choices=(
        (time(hour=9, minute=0, second=0), '9:00 AM'),
        (time(hour=9, minute=30, second=0), '9:30 AM'),
        (time(hour=10, minute=0, second=0), '10:00 AM'),
        (time(hour=10, minute=30, second=0), '10:30 AM'),
        (time(hour=11, minute=0, second=0), '11:00 AM'),
        (time(hour=11, minute=30, second=0), '11:30 AM'),
        (time(hour=12, minute=0, second=0), '12:00 PM'),
        (time(hour=12, minute=30, second=0), '12:30 PM'),
        (time(hour=13, minute=0, second=0), '1:00 PM'),
        (time(hour=13, minute=30, second=0), '1:30 PM'),
        (time(hour=14, minute=0, second=0), '2:00 PM'),
        (time(hour=14, minute=30, second=0), '2:30 PM'),
        (time(hour=15, minute=0, second=0), '3:00 PM'),
        (time(hour=15, minute=30, second=0), '3:30 PM'),
        (time(hour=16, minute=0, second=0), '4:00 PM'),
        (time(hour=16, minute=30, second=0), '4:30 PM'),
        (time(hour=17, minute=0, second=0), '5:00 PM'),
        (time(hour=17, minute=30, second=0), '5:30 PM'),
        (time(hour=18, minute=0, second=0), '6:00 PM'),
        (time(hour=18, minute=30, second=0), '6:30 PM'),
        (time(hour=19, minute=0, second=0), '7:00 PM'),
        (time(hour=19, minute=30, second=0), '7:30 PM'),
        (time(hour=20, minute=0, second=0), '8:00 PM'),
    ))

    def clean_hora_inicio(self):
        """
        El form capturado por usuario regresa str entonces convierte a objeto time
        :return: Objeto time de datetime
        """
        hora_inicio = self.cleaned_data.get('hora_inicio')
        # print(f'clean hora inicio {hora_inicio}')
        return datetime.strptime(hora_inicio, '%H:%M:%S').time()

    def clean_inicio(self):
        inicio = self.cleaned_data.get('inicio')
        if inicio.date().weekday() >= 5:
            raise forms.ValidationError("Elija fecha de inicio de préstamo entre semana.")

        if inicio.date() < (date.today() + timedelta(days=3)):
            raise forms.ValidationError("Elija una fecha tres días a partir de hoy.")

        # print(f'clean inicio {inicio}')
        return inicio