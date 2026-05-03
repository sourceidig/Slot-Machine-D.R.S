from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('control', '0011_cierre_maquina'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='controllecturas',
            name='uniq_control_por_sucursal_fecha',
        ),
    ]
