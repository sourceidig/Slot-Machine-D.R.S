from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('control', '0011_cierre_maquina'),
    ]

    operations = [
        # MySQL (RDS) usa el unique index (sucursal_id, fecha_trabajo) para respaldar
        # el FK en sucursal_id. Si no existe un índice regular previo, MySQL rechaza
        # la eliminación con error 1553. Creamos uno explícito antes de borrar el constraint.
        migrations.AddIndex(
            model_name='controllecturas',
            index=models.Index(fields=['sucursal'], name='ctrl_lecturas_sucursal_idx'),
        ),
        migrations.RemoveConstraint(
            model_name='controllecturas',
            name='uniq_control_por_sucursal_fecha',
        ),
    ]
