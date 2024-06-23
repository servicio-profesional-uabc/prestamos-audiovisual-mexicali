from datetime import date, timedelta, datetime, time

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.core.validators import MaxLengthValidator
from django.utils.timezone import make_aware
from phonenumber_field.formfields import PhoneNumberField

from .models import Carrito, Perfil, Prestatario, Ubicacion, CorresponsableOrden
from .models import Orden, EstadoOrden


class CambiarEstadoCorresponsableOrdenForm(forms.ModelForm):
    class Meta:
        model = CorresponsableOrden
        fields = ['estado']
        widgets = {
            'estado': forms.Select(choices=[
                (EstadoOrden.CANCELADA, 'Cancelada'),
                (EstadoOrden.APROBADA, 'Aprobada')
            ])
        }


class CambiarEstadoOrdenForm(forms.ModelForm):
    class Meta:
        model = Orden
        fields = ['estado']
        widgets = {
            'estado': forms.Select(choices=[
                (EstadoOrden.CANCELADA, 'Cancelada'),
                (EstadoOrden.APROBADA, 'Aprobada')
            ])
        }


class UpdateUserForm(forms.ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['email']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email.endswith("@uabc.edu.mx"):
            raise forms.ValidationError("El correo debe ser institucional de la UABC.")
        return email

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


class CorresponsableForm(forms.ModelForm):
    corresponsables = forms.ModelMultipleChoiceField(
        queryset=Prestatario.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Corresponsables"
    )

    class Meta:
        model = Carrito
        fields = ['corresponsables']

    def __init__(self, *args, **kwargs):
        carrito = kwargs.get('instance')

        # TODO: reemplazar este por get_of_404 o similar
        materia = kwargs.pop('materia', None)
        super(CorresponsableForm, self).__init__(*args, **kwargs)

        if materia and carrito:
            alumnos = materia.alumnos()
            self.fields['corresponsables'].queryset = alumnos
            self.fields['corresponsables'].initial = carrito._corresponsables.all()


# Forms para Filtro (asigna los datos al modelo Carrito, primera parte seccion del carrito)
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
        fields = ['inicio', 'nombre', 'materia', 'lugar', 'descripcion', 'lugar', 'descripcion_lugar',
                  '_corresponsables']

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

    lugar = forms.ChoiceField(required=True, choices=(
        (Ubicacion.CAMPUS, "En el Campus"),
        (Ubicacion.EXTERNO, "Fuera del Campus"),
    ))

    def clean_hora_inicio(self):
        """
        Limpia y valida la hora de inicio capturada por el usuario, este regresa str entonces convierte a objeto time
        :return: Objeto time de datetime
        """
        hora_inicio = self.cleaned_data.get('hora_inicio')
        # print(f'clean hora inicio {hora_inicio}')
        return datetime.strptime(hora_inicio, '%H:%M:%S').time()

    def clean_inicio(self):
        """
        Limpia y valida la fecha de inicio capturado por el usuario.
        :return: Objeto datetime
        """
        inicio = self.cleaned_data.get('inicio')
        if inicio.date().weekday() >= 5:
            raise forms.ValidationError("Elige fecha de inicio de préstamo entre semana.")

        if inicio.date() < (date.today() + timedelta(days=3)):
            raise forms.ValidationError("Elige una fecha tres días a partir de hoy.")

        # print(f'clean inicio {inicio}')
        return inicio

    def clean(self):
        cleaned_data = super().clean()
        inicio = cleaned_data.get('inicio')
        hora_inicio = cleaned_data.get('hora_inicio')
        duracion = cleaned_data.get('duracion')

        if not inicio:
            return

        if not hora_inicio:
            return

        if not duracion:
            return

        tiempo_duracion = int(duracion)
        fecha_inicio = datetime.combine(inicio, hora_inicio)
        fecha_final = make_aware(fecha_inicio + timedelta(hours=tiempo_duracion))

        if fecha_final.date().weekday() >= 5:
            raise (forms.ValidationError("La fecha final del préstamo es en fin de semana. Intente de nuevo."))

        if fecha_final.hour > 20 or fecha_final.hour < 9:
            raise (forms.ValidationError(
                "La fecha final del préstamo es fuera del horario de atención. Intente de nuevo."))

        return cleaned_data
