from django.db import models
from django.contrib.auth.models import User
from datetime import date
from django.utils import timezone
from django.urls import reverse
from django.db.models.signals import post_save
from django.dispatch import receiver

class Pnf(models.Model):
    nombre_pnf = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre_pnf


class Trayecto(models.Model):
    nombre_trayecto = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre_trayecto


class Seccion(models.Model):
    seccion_estudiante = models.CharField(max_length=30, null=True)

    def __str__(self):
        return self.seccion_estudiante


class Proyecto(models.Model):
    ESTADOS = (
        ("PENDIENTE", "Pendiente"),
        ("EN_REVISION", "En revisión"),
        ("APROBADO", "Aprobado"),
        ("RECHAZADO", "Rechazado"),
    )

    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    trayecto = models.ForeignKey(Trayecto, on_delete=models.CASCADE)
    pnf = models.ForeignKey(Pnf, on_delete=models.CASCADE)
    seccion = models.ForeignKey(Seccion, null=True, on_delete=models.CASCADE)
    tutor = models.CharField(max_length=120)
    titulo = models.TextField()
    descripcion = models.TextField()
    cedula = models.TextField(null=True)
    palabras_clave = models.TextField()
    autores = models.TextField()
    tutor_metodologico = models.TextField(null=True)
    estado = models.TextField(null=True, blank=True)
    nota = models.PositiveSmallIntegerField(null=True, blank=True)
    municipio = models.TextField(null=True)
    parroquia = models.TextField(null=True)
    nombre_comunidad = models.TextField(null=True)
    fecha_creacion = models.DateField(default=date.today)
    fecha_subido = models.DateField(auto_now_add=True)
    archivo = models.FileField(upload_to="proyectos/", blank=True, null=True)
    revisado = models.BooleanField(default=False, null=True)

    def __str__(self):
        return self.titulo


class Momento(models.Model):
    MOMENT_CHOICES = (
        ("MOMENTO I", "MOMENTO I"),
        ("MOMENTO II", "MOMENTO II"),
        ("MOMENTO III", "MOMENTO III"),
        ("MOMENTO IV", "MOMENTO IV"),
    )
    REVISION_CHOICES = (
        ("PENDIENTE", "Pendiente"),
        ("CORREGIDO", "Corregido"),
        ("CON_CORRECCIONES", "Con correcciones"),
    )
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name='momentos')
    nombre = models.CharField(max_length=20, choices=MOMENT_CHOICES)
    estado_revision = models.CharField(max_length=20, choices=REVISION_CHOICES, default='PENDIENTE')
    feedback = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("proyecto", "nombre")
        ordering = ['nombre']

    def __str__(self):
        return f"{self.proyecto_id} - {self.nombre}"

    def latest_version(self):
        return self.versions.order_by('-version', '-created_at').first()


class MomentoVersion(models.Model):
    momento = models.ForeignKey(Momento, on_delete=models.CASCADE, related_name='versions')
    archivo = models.FileField(upload_to="momentos/")
    version = models.PositiveIntegerField(default=1)
    etiqueta = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    ORIGEN_CHOICES = (
        ('ESTUDIANTE', 'Estudiante'),
        ('ADMIN', 'Administrador'),
    )
    origen = models.CharField(max_length=12, choices=ORIGEN_CHOICES, default='ESTUDIANTE')
    subido_por = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='versiones_subidas')

    class Meta:
        ordering = ['-version', '-created_at']

    def save(self, *args, **kwargs):
        if not self.pk and (self.version is None or self.version == 1):
            last = self.momento.versions.order_by('-version').first()
            self.version = (last.version + 1) if last else 1
        if not self.etiqueta:
            self.etiqueta = f"V{self.version}.0"
        super().save(*args, **kwargs)


class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    proyecto = models.ForeignKey('Proyecto', on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)
    preview = models.CharField(max_length=255)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Notif to {self.recipient_id} -> Proyecto {self.proyecto_id}'

    def get_absolute_url(self):
        if self.proyecto_id:
            return reverse('panel:project_detail', args=[self.proyecto_id])
        return '#'


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    photo = models.ImageField(upload_to='profiles/', null=True, blank=True)
    failed_login_attempts = models.PositiveSmallIntegerField(default=0)
    locked_at = models.DateTimeField(null=True, blank=True)
    # Papelera
    is_trashed = models.BooleanField(default=False)
    trashed_at = models.DateTimeField(null=True, blank=True)
    # Roles de usuario (sin DOCENTE)
    ROLE_CHOICES = (
        ('ESTUDIANTE', 'Estudiante'),
        ('ADMIN', 'Administrador'),
    )
    role = models.CharField(max_length=12, choices=ROLE_CHOICES, default='ESTUDIANTE')

    def __str__(self):
        return f"Perfil de {self.user.username}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    Profile.objects.get_or_create(user=instance)