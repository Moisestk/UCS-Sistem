from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox
from .models import Proyecto, Trayecto, Pnf, Seccion, Estado
import os

def validate_document_file(file):
    """
    Valida que el archivo sea PDF o DOCX
    """
    if not file:
        return
    
    # Obtener la extensión del archivo
    ext = os.path.splitext(file.name)[1].lower()
    allowed_extensions = ['.pdf', '.docx']
    
    if ext not in allowed_extensions:
        raise ValidationError(
            'Solo se permiten archivos PDF (.pdf) y Word (.docx). '
            f'El archivo seleccionado tiene extensión: {ext}'
        )
    
    # Validar tamaño del archivo (máximo 10MB)
    if file.size > 10 * 1024 * 1024:  # 10MB
        raise ValidationError('El archivo no puede ser mayor a 10MB.')

class PnfForm(forms.ModelForm):
    class Meta:
        model = Pnf
        fields = "__all__"
        widgets = {
            'nombre_pnf': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Enfermería Integral Comunitaria',
                'maxlength': '100'
            })
        }
    
    def clean_nombre_pnf(self):
        nombre = self.cleaned_data.get('nombre_pnf')
        if nombre:
            nombre = nombre.strip()
            if len(nombre) < 3:
                raise ValidationError('El nombre del PNF debe tener al menos 3 caracteres.')
            if len(nombre) > 100:
                raise ValidationError('El nombre del PNF no puede exceder 100 caracteres.')
            
            # Verificar duplicados (excluyendo la instancia actual si estamos editando)
            queryset = Pnf.objects.filter(nombre_pnf__iexact=nombre)
            if self.instance and self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            
            if queryset.exists():
                raise ValidationError('Ya existe un PNF con este nombre.')
        
        return nombre

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
        widgets = {
            'archivo': forms.FileInput(attrs={
                'accept': '.pdf,.docx',
                'class': 'form-control'
            }),
            'estado': forms.Select(attrs={
                'class': 'form-control'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Cargar solo estados activos
        self.fields['estado'].queryset = Estado.objects.filter(activo=True).order_by('nombre')
    
    def clean_archivo(self):
        archivo = self.cleaned_data.get('archivo')
        validate_document_file(archivo)
        return archivo

# -------- Registro seguro (dos pasos) --------
class RegistrationStep1Form(forms.Form):
    first_name = forms.CharField(label='Nombre', max_length=150)
    last_name = forms.CharField(label='Apellido', max_length=150)
    email = forms.EmailField(label='Correo')
    password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repetir contraseña', widget=forms.PasswordInput)
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())

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
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())

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
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())