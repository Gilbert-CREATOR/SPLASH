# Generated migration for stock_virtual field

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pos', '0002_alter_producto_categoria'),
    ]

    operations = [
        migrations.AddField(
            model_name='producto',
            name='stock_virtual',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]
