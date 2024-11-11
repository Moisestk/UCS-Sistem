from django.db import models
from django.contrib.auth.models import User

# Create your models here.




class Pnf (models.Model):
    nombre_pnf = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre_pnf
    
    
class Trayecto (models.Model):
    nombre_trayecto = models.CharField(max_length=100)
    
    def __str__(self):
        return self.nombre_trayecto
    
class Seccion (models.Model):
    seccion_estudiante = models.CharField(max_length=30, null=True)
    
    def __str__(self):
        return self.seccion_estudiante 
    
class Proyecto(models.Model):
    usuario= models.ForeignKey(User,on_delete=models.CASCADE)
    trayecto= models.ForeignKey(Trayecto,on_delete=models.CASCADE)
    pnf= models.ForeignKey(Pnf,on_delete=models.CASCADE)
    seccion = models.ForeignKey(Seccion, null=True, on_delete=models.CASCADE)
    tutor= models.CharField(max_length=120)
    titulo = models.TextField()
    descripcion = models.TextField()
    cedula = models.TextField(null=True)
    palabras_clave = models.TextField()
    autores = models.TextField()
    tutor_metodologico = models.TextField(null=True)
    estado = models.TextField(null=True)
    municipio = models.TextField(null=True)
    parroquia = models.TextField(null=True)
    nombre_comunidad = models.TextField(null=True)
    fecha_creacion = models.DateField()
    fecha_subido = models.DateField(auto_now_add=True)
    archivo= models.FileField(upload_to="media/proyectos/", blank=True, null=True)
    revisado = models.BooleanField(default=False, null=True)

    def __str__(self):
       return self.titulo
      
    
    