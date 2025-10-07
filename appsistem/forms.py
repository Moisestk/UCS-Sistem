from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from captcha.fields import CaptchaField
from .models import Proyecto, Trayecto, Pnf, Seccion

class PnfForm(forms.ModelForm):
    class Meta:
        model = Pnf
        fields = "__all__"

class TrayectoForm(forms.ModelForm):
    class Meta:
        model = Trayecto
        fields = "__all__"

class SeccionForm(forms.ModelForm):
    class Meta:
        model = Seccion
        fields = "__all__"

class ProyectoForm(forms.ModelForm):
    class Meta:
        model = Proyecto
        exclude = ['fecha_subida']

# -------- Registro seguro (dos pasos) --------
class RegistrationStep1Form(forms.Form):
    first_name = forms.CharField(label='Nombre', max_length=150)
    last_name = forms.CharField(label='Apellido', max_length=150)
    email = forms.EmailField(label='Correo')
    password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repetir contraseña', widget=forms.PasswordInput)
    captcha = CaptchaField()

    def clean(self):
        data = super().clean()
        p1 = data.get('password1')
        p2 = data.get('password2')
        if p1 != p2:
            raise ValidationError('Las contraseñas no coinciden.')
        # Reglas de fortaleza
        if len(p1 or '') < 8:
            raise ValidationError('La contraseña debe tener al menos 8 caracteres.')
        if not any(c.islower() for c in p1):
            raise ValidationError('La contraseña debe incluir al menos una letra minúscula.')
        if not any(c.isupper() for c in p1):
            raise ValidationError('La contraseña debe incluir al menos una letra mayúscula.')
        if not any(c.isdigit() for c in p1):
            raise ValidationError('La contraseña debe incluir al menos un número.')
        # Email único
        email = (data.get('email') or '').strip()
        if email and User.objects.filter(email__iexact=email).exists():
            raise ValidationError('Este correo ya está registrado.')
        return data

class RegistrationStep2Form(forms.Form):
    username = forms.CharField(
        label='Cédula de identidad (solo números, 7 u 8 dígitos)',
        min_length=7,
        max_length=8,
    )
    photo = forms.ImageField(label='Foto de perfil', required=False)

    def clean_username(self):
        username = (self.cleaned_data.get('username') or '').strip()
        if not username.isdigit():
            raise ValidationError('La cédula debe ser numérica (solo dígitos).')
        if len(username) not in (7, 8):
            raise ValidationError('La cédula debe tener 7 u 8 dígitos.')
        if User.objects.filter(username=username).exists():
            raise ValidationError('Esta cédula ya está registrada como usuario.')
        return username

# -------- Login con captcha --------
class LoginWithCaptchaForm(AuthenticationForm):
    captcha = CaptchaField()