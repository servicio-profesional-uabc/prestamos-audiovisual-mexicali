from datetime import date, timedelta, datetime

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from phonenumber_field.formfields import PhoneNumberField

from .models import Carrito, Materia, Perfil


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
class DateInput(forms.DateInput):
    input_type = 'date'


class FiltrosForm(forms.ModelForm):
    """
    Form para filtrar catalogo/carrito
    """

    class Meta:
        model = Carrito
        fields = ['inicio', 'materia']

    materia = forms.ModelChoiceField(required=True, queryset=Materia.objects.all())

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
    ))

    def clean_hora_inicio(self):
        hora_inicio = self.cleaned_data.get('hora_inicio')
        duracion = self.cleaned_data.get('duracion')
        inicio = self.cleaned_data.get('inicio')

        hora_inicio_datetime = datetime.strptime(hora_inicio, '%H:%M:%S')
        hora = datetime.time(hora_inicio_datetime)
        tiempo_duracion = int(duracion)
        fecha_inicio = datetime.combine(inicio, hora)
        fecha_final = fecha_inicio + timedelta(hours=tiempo_duracion)

        INICIO_HORARIO = 7
        FIN_HORARIO = 20

        if not (INICIO_HORARIO <= fecha_final.time().hour <= FIN_HORARIO):
            raise forms.ValidationError(
                'La combinación de hora y duración del préstamo marcan fuera de horario de atención. Intente de nuevo.')

        if fecha_final.date().weekday() >= 5:
            raise forms.ValidationError(
                'La fecha de devolución del préstamo es en fin de semana. Intente de nuevo cambiándo la duración del préstamo.')

        return hora_inicio

    def clean_inicio(self):
        # [x] Agregar fecha inicio agregarle su hora de inicio
        # [x] Sumarle la duracion de horas a dicha fecha
        # [X] Validar que sea elegido en fecha sea 3 dias de anticipacion
        # [X] Validar que inicio sea entre semana (no importa que pase por fin eso se hace extra al hacer solicitud)
        # [X] Guardar dicha fecha final en la variable final de carrito

        # Si fecha de inicio de préstamo es antes de los tres días de anticipación mostrar error.
        inicio = self.cleaned_data.get('inicio')

        if inicio.date().weekday() >= 5:
            raise forms.ValidationError("Por favor elija fecha de inicio de préstamo entre semana.")

        if inicio.date() < (date.today() + timedelta(days=3)):
            raise forms.ValidationError("Por favor elija una fecha tres días a partir de hoy.")

        return inicio
