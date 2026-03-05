from django.db import migrations, models


def migrate_old_roles(apps, schema_editor):
    """'usuario' → 'gerente'"""
    Usuario = apps.get_model('control', 'Usuario')
    Usuario.objects.filter(role='usuario').update(role='gerente')


def reverse_migrate_roles(apps, schema_editor):
    Usuario = apps.get_model('control', 'Usuario')
    Usuario.objects.filter(role='gerente').update(role='usuario')


class Migration(migrations.Migration):

    dependencies = [
        ('control', '0001_initial'),
    ]

    operations = [
        # 1. Nuevos ROLE_CHOICES y default
        migrations.AlterField(
            model_name='usuario',
            name='role',
            field=models.CharField(
                max_length=20,
                choices=[
                    ('admin',      'Administrador'),
                    ('gerente',    'Gerente'),
                    ('supervisor', 'Supervisor'),
                    ('tecnico',    'Técnico'),
                    ('encargado',  'Encargado'),
                    ('asistente',  'Asistente'),
                ],
                default='asistente',
                verbose_name='Rol',
            ),
        ),

        # 2. Migrar datos: 'usuario' → 'gerente'
        migrations.RunPython(migrate_old_roles, reverse_migrate_roles),

        # 3. Agregar M2M sucursales
        # (NO hay RemoveField porque sucursal nunca existió en Usuario en el 0001)
        migrations.AddField(
            model_name='usuario',
            name='sucursales',
            field=models.ManyToManyField(
                to='control.Sucursal',
                blank=True,
                related_name='usuarios_asignados',
                verbose_name='Sucursales Asignadas',
            ),
        ),
    ]
