from django import forms
from .models import Proyecto, Trayecto, Pnf, Seccion

class PnfForm (forms.ModelForm):
    class Meta :
        model = Pnf 
        fields = "__all__"

        
class TrayectoForm (forms.ModelForm):
    class Meta :
        model = Trayecto 
        fields = "__all__"


class SeccionForm (forms.ModelForm):
    class Meta :
        model = Seccion
        fields = "__all__"
        

class ProyectoForm(forms.ModelForm):
    class Meta :
        model = Proyecto
        exclude = ['fecha_subida']
        
    

