# Generated manually
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('appsistem', '0025_populate_estados'),
    ]

    operations = [
        # Agregar el campo estado_revision
        migrations.AddField(
            model_name='proyecto',
            name='estado_revision',
            field=models.CharField(max_length=20, choices=[('PENDIENTE', 'Pendiente'), ('EN_REVISION', 'En revisión'), ('APROBADO', 'Aprobado'), ('RECHAZADO', 'Rechazado')], default='PENDIENTE', verbose_name='Estado de Revisión'),
        ),
    ]
