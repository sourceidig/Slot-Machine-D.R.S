from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('control', '0012_remove_uniq_control_por_sucursal_fecha'),
    ]

    operations = [
        migrations.AddField(
            model_name='turno',
            name='ultima_url',
            field=models.CharField(blank=True, default='', max_length=500),
        ),
    ]
