from django.db import migrations


def crear_tecnicos(apps, schema_editor):
    Tecnico = apps.get_model('tecnicos', 'Tecnico')
    if Tecnico.objects.exists():
        return
    Tecnico.objects.bulk_create([
        Tecnico(nombre='Carlos Pérez', especialidad='Redes'),
        Tecnico(nombre='Laura Gómez', especialidad='Hardware'),
        Tecnico(nombre='Andrés Rojas', especialidad='Software'),
    ])


class Migration(migrations.Migration):

    dependencies = [
        ('tecnicos', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(crear_tecnicos, migrations.RunPython.noop),
    ]
