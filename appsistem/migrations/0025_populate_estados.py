# Generated manually
from django.db import migrations

def populate_estados(apps, schema_editor):
    """Poblar la tabla Estado con los estados de Venezuela"""
    Estado = apps.get_model('appsistem', 'Estado')
    
    estados_venezuela = [
        {'nombre': 'Amazonas', 'codigo': 'AMZ'},
        {'nombre': 'Anzoátegui', 'codigo': 'ANZ'},
        {'nombre': 'Apure', 'codigo': 'APU'},
        {'nombre': 'Aragua', 'codigo': 'ARA'},
        {'nombre': 'Barinas', 'codigo': 'BAR'},
        {'nombre': 'Bolívar', 'codigo': 'BOL'},
        {'nombre': 'Carabobo', 'codigo': 'CAR'},
        {'nombre': 'Cojedes', 'codigo': 'COJ'},
        {'nombre': 'Delta Amacuro', 'codigo': 'DAM'},
        {'nombre': 'Falcón', 'codigo': 'FAL'},
        {'nombre': 'Guárico', 'codigo': 'GUA'},
        {'nombre': 'La Guaira', 'codigo': 'LAG'},
        {'nombre': 'Lara', 'codigo': 'LAR'},
        {'nombre': 'Mérida', 'codigo': 'MER'},
        {'nombre': 'Miranda', 'codigo': 'MIR'},
        {'nombre': 'Monagas', 'codigo': 'MON'},
        {'nombre': 'Nueva Esparta', 'codigo': 'NES'},
        {'nombre': 'Portuguesa', 'codigo': 'POR'},
        {'nombre': 'Sucre', 'codigo': 'SUC'},
        {'nombre': 'Táchira', 'codigo': 'TAC'},
        {'nombre': 'Trujillo', 'codigo': 'TRU'},
        {'nombre': 'Yaracuy', 'codigo': 'YAR'},
        {'nombre': 'Zulia', 'codigo': 'ZUL'},
    ]
    
    for estado_data in estados_venezuela:
        Estado.objects.get_or_create(
            nombre=estado_data['nombre'],
            defaults={'codigo': estado_data['codigo']}
        )

def reverse_populate_estados(apps, schema_editor):
    Estado = apps.get_model('appsistem', 'Estado')
    Estado.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('appsistem', '0024_create_estado_model'),
    ]

    operations = [
        migrations.RunPython(populate_estados, reverse_populate_estados),
    ]
