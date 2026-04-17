# Generated migration for ventas_pendientes field

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pos', '0004_add_stock_virtual'),
    ]

    operations = [
        migrations.AddField(
            model_name='producto',
            name='ventas_pendientes',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]
