from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ("control", "0033_remove_cuadraturacajadiaria_unique_cuadratura_por_dia_and_more"),  # <-- cambia esto por tu última migración real
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                ALTER TABLE control_cuadraturacajadiaria
                MODIFY creado_el DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                MODIFY actualizado_el DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;
            """,
            reverse_sql="""
                ALTER TABLE control_cuadraturacajadiaria
                MODIFY creado_el DATETIME NOT NULL,
                MODIFY actualizado_el DATETIME NOT NULL;
            """
        )
    ]
