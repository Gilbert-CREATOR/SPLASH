from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Create migration for stock_virtual field'

    def handle(self, *args, **options):
        self.stdout.write('🔄 Creating migration for stock_virtual field...')
        
        # Create the migration manually
        migration_content = '''
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
'''
        
        # Write migration file
        import os
        from datetime import datetime
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        migration_file = f'pos/migrations/0004_add_stock_virtual.py'
        
        os.makedirs('pos/migrations', exist_ok=True)
        
        with open(migration_file, 'w') as f:
            f.write(migration_content)
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ Migration file created: {migration_file}')
        )
        
        self.stdout.write(
            self.style.STYLE('Now run: python3 manage.py migrate')
        )
