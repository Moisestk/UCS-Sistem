#app de terceros
from import_export import resources
from import_export.admin import ImportExportModelAdmin, ExportActionMixin

from django.contrib import admin
from .models import Pnf,Proyecto,Trayecto,Seccion


# Register your models here.
class ProyectoResourse(resources.ModelResource):
    fields = (
        'autores',
        'pnf',
        'trayecto',
        'titulo',
        'fecha',
        'archivo'
        
    )
    class Meta:
        model = Proyecto

@admin.register(Proyecto)
class ProyectoAdmin (ImportExportModelAdmin, ExportActionMixin):
    pass
    resource_class = ProyectoResourse
    search_fields = ('pnf__nombre_pnf','trayecto__nombre_trayecto', 'autores','tutor','cedula',)
    list_display = ('autores', 'cedula','pnf','trayecto', 'tutor', 'fecha_subido' ) 
    list_filter = ('pnf', 'trayecto', 'tutor', 'fecha_subido', )



admin.site.register(Seccion)

admin.site.register(Pnf)

admin.site.register(Trayecto)
