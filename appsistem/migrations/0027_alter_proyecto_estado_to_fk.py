# Generated manually
from django.db import migrations, models
import django.db.models.deletion

def migrate_estado_data(apps, schema_editor):
    """Migrar datos existentes del campo estado a la nueva tabla Estado"""
    Proyecto = apps.get_model('appsistem', 'Proyecto')
    Estado = apps.get_model('appsistem', 'Estado')
    
    # Mapeo de valores existentes a nombres de estados
    estado_mapping = {
        'FALCON': 'Falcón',
        'La Guaira': 'La Guaira',
        'Guárico': 'Guárico',
        'Anzoátegui': 'Anzoátegui',
        'Barinas': 'Barinas',
        'Bolívar': 'Bolívar',
        'Carabobo': 'Carabobo',
        'Cojedes': 'Cojedes',
        'Delta Amacuro': 'Delta Amacuro',
        'Amazonas': 'Amazonas',
        'Apure': 'Apure',
        'Aragua': 'Aragua',
        'Lara': 'Lara',
        'Mérida': 'Mérida',
        'Miranda': 'Miranda',
        'Monagas': 'Monagas',
        'Nueva Esparta': 'Nueva Esparta',
        'Portuguesa': 'Portuguesa',
        'Sucre': 'Sucre',
        'Táchira': 'Táchira',
        'Trujillo': 'Trujillo',
        'Yaracuy': 'Yaracuy',
        'Zulia': 'Zulia',
    }
    
    # Obtener todos los valores únicos de estado que existen
    estados_existentes = Proyecto.objects.exclude(estado__isnull=True).exclude(estado='').values_list('estado', flat=True).distinct()
    
    # Crear estados que no existen
    for estado_valor in estados_existentes:
        nombre_estado = estado_mapping.get(estado_valor, estado_valor)
        estado_obj, created = Estado.objects.get_or_create(
            nombre=nombre_estado,
            defaults={'codigo': estado_valor[:3].upper() if len(estado_valor) >= 3 else estado_valor.upper()}
        )

def reverse_migrate_estado_data(apps, schema_editor):
    pass

def migrate_estado_fk_data(apps, schema_editor):
    """Migrar datos del campo estado al campo estado_id"""
    Proyecto = apps.get_model('appsistem', 'Proyecto')
    Estado = apps.get_model('appsistem', 'Estado')
    
    estado_mapping = {
        'FALCON': 'Falcón',
        'La Guaira': 'La Guaira',
        'Guárico': 'Guárico',
        'Anzoátegui': 'Anzoátegui',
        'Barinas': 'Barinas',
        'Bolívar': 'Bolívar',
        'Carabobo': 'Carabobo',
        'Cojedes': 'Cojedes',
        'Delta Amacuro': 'Delta Amacuro',
        'Amazonas': 'Amazonas',
        'Apure': 'Apure',
        'Aragua': 'Aragua',
        'Lara': 'Lara',
        'Mérida': 'Mérida',
        'Miranda': 'Miranda',
        'Monagas': 'Monagas',
        'Nueva Esparta': 'Nueva Esparta',
        'Portuguesa': 'Portuguesa',
        'Sucre': 'Sucre',
        'Táchira': 'Táchira',
        'Trujillo': 'Trujillo',
        'Yaracuy': 'Yaracuy',
        'Zulia': 'Zulia',
    }
    
    for proyecto in Proyecto.objects.all():
        if proyecto.estado:
            nombre_estado = estado_mapping.get(proyecto.estado, proyecto.estado)
            try:
                estado_obj = Estado.objects.get(nombre=nombre_estado)
                proyecto.estado_id = estado_obj.id
                proyecto.save(update_fields=['estado_id'])
            except Estado.DoesNotExist:
                proyecto.estado_id = None
                proyecto.save(update_fields=['estado_id'])

class Migration(migrations.Migration):
    dependencies = [
        ('appsistem', '0026_add_estado_revision_field'),
    ]

    operations = [
        # Migrar datos existentes
        migrations.RunPython(migrate_estado_data, reverse_migrate_estado_data),
        
        # Agregar campo estado_id temporal
        migrations.AddField(
            model_name='proyecto',
            name='estado_id',
            field=models.IntegerField(null=True, blank=True),
        ),
        
        # Migrar datos del campo estado al campo estado_id
        migrations.RunPython(
            migrate_estado_fk_data,
            reverse_migrate_estado_data
        ),
        
        # Eliminar campo estado original
        migrations.RemoveField(
            model_name='proyecto',
            name='estado',
        ),
        
        # Renombrar estado_id a estado
        migrations.RenameField(
            model_name='proyecto',
            old_name='estado_id',
            new_name='estado',
        ),
        
        # Cambiar tipo de campo a ForeignKey
        migrations.AlterField(
            model_name='proyecto',
            name='estado',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='appsistem.estado', verbose_name='Estado de Venezuela'),
        ),
    ]
