from django.core.management.base import BaseCommand
from django.conf import settings
import os
import shutil
from datetime import datetime

class Command(BaseCommand):
    help = 'Create complete system backup'

    def handle(self, *args, **options):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = f'backups/backup_{timestamp}'
        
        # Create backup directory
        os.makedirs(backup_dir, exist_ok=True)
        
        self.stdout.write(f'🔄 Creating backup in {backup_dir}...')
        
        # Backup database
        db_path = settings.DATABASES['default']['NAME']
        if os.path.exists(db_path):
            db_backup = os.path.join(backup_dir, 'db.sqlite3')
            shutil.copy2(db_path, db_backup)
            self.stdout.write(self.style.SUCCESS('✅ Database backed up'))
        
        # Backup media files
        if os.path.exists('media'):
            media_backup = os.path.join(backup_dir, 'media')
            shutil.copytree('media', media_backup)
            self.stdout.write(self.style.SUCCESS('✅ Media files backed up'))
        
        # Backup templates
        if os.path.exists('templates'):
            templates_backup = os.path.join(backup_dir, 'templates')
            shutil.copytree('templates', templates_backup)
            self.stdout.write(self.style.SUCCESS('✅ Templates backed up'))
        
        # Backup pos app
        if os.path.exists('pos'):
            pos_backup = os.path.join(backup_dir, 'pos')
            shutil.copytree('pos', pos_backup)
            self.stdout.write(self.style.SUCCESS('✅ POS app backed up'))
        
        # Create backup info
        info_file = os.path.join(backup_dir, 'backup_info.txt')
        with open(info_file, 'w') as f:
            f.write('Backup created: {}\n'.format(datetime.now()))
            f.write('Backup directory: {}\n'.format(backup_dir))
            f.write('Database: {}\n'.format(db_path))
            import sys
            f.write('Python version: {}\n'.format(sys.version))
            import django
            f.write('Django version: {}\n'.format(django.VERSION))
        
        self.stdout.write(
            self.style.SUCCESS('✅ Backup completed successfully in {}'.format(backup_dir))
        )
