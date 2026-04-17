from django.core.management.base import BaseCommand
from django.conf import settings
import os
import shutil
from datetime import datetime

class Command(BaseCommand):
    help = 'Restore system from backup'

    def add_arguments(self, parser):
        parser.add_argument('backup_path', type=str, help='Path to backup directory')

    def handle(self, *args, **options):
        backup_path = options['backup_path']
        
        if not os.path.exists(backup_path):
            self.stdout.write(
                self.style.ERROR(f'❌ Backup directory {backup_path} does not exist')
            )
            return
        
        self.stdout.write(f'🔄 Restoring from {backup_path}...')
        
        # Stop confirmation
        confirm = input('⚠️  This will overwrite current system. Are you sure? (yes/no): ')
        if confirm.lower() != 'yes':
            self.stdout.write('❌ Restore cancelled')
            return
        
        # Restore database
        db_backup = os.path.join(backup_path, 'db.sqlite3')
        if os.path.exists(db_backup):
            db_path = settings.DATABASES['default']['NAME']
            shutil.copy2(db_backup, db_path)
            self.stdout.write(self.style.SUCCESS('✅ Database restored'))
        
        # Restore media files
        media_backup = os.path.join(backup_path, 'media')
        if os.path.exists(media_backup):
            if os.path.exists('media'):
                shutil.rmtree('media')
            shutil.copytree(media_backup, 'media')
            self.stdout.write(self.style.SUCCESS('✅ Media files restored'))
        
        # Restore templates
        templates_backup = os.path.join(backup_path, 'templates')
        if os.path.exists(templates_backup):
            if os.path.exists('templates'):
                shutil.rmtree('templates')
            shutil.copytree(templates_backup, 'templates')
            self.stdout.write(self.style.SUCCESS('✅ Templates restored'))
        
        # Restore pos app
        pos_backup = os.path.join(backup_path, 'pos')
        if os.path.exists(pos_backup):
            if os.path.exists('pos'):
                shutil.rmtree('pos')
            shutil.copytree(pos_backup, 'pos')
            self.stdout.write(self.style.SUCCESS('✅ POS app restored'))
        
        self.stdout.write(
            self.style.SUCCESS('✅ System restore completed successfully')
        )
