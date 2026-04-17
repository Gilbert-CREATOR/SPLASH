from django.core.management.base import BaseCommand
import os
import stat

class Command(BaseCommand):
    help = 'Fix file permissions for the project'

    def handle(self, *args, **options):
        self.stdout.write('🔧 FIXING FILE PERMISSIONS')
        self.stdout.write('=' * 40)
        
        # Fix common permission issues
        files_to_fix = [
            'db.sqlite3',
            'manage.py',
            'requirements.txt'
        ]
        
        dirs_to_fix = [
            'media',
            'templates',
            'pos',
            'static',
            'backups'
        ]
        
        # Fix file permissions
        for file_name in files_to_fix:
            if os.path.exists(file_name):
                try:
                    # Read/write for owner, read for others
                    os.chmod(file_name, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
                    self.stdout.write(self.style.SUCCESS(f'✅ Fixed permissions for {file_name}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'❌ Error fixing {file_name}: {e}'))
        
        # Fix directory permissions
        for dir_name in dirs_to_fix:
            if os.path.exists(dir_name):
                try:
                    # Read/write/execute for owner, read/execute for others
                    os.chmod(dir_name, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
                    self.stdout.write(self.style.SUCCESS(f'✅ Fixed permissions for {dir_name}/'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'❌ Error fixing {dir_name}/: {e}'))
        
        # Make management commands executable
        management_dir = 'pos/management/commands'
        if os.path.exists(management_dir):
            for file_name in os.listdir(management_dir):
                file_path = os.path.join(management_dir, file_name)
                if os.path.isfile(file_path):
                    try:
                        os.chmod(file_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
                        self.stdout.write(self.style.SUCCESS(f'✅ Made {file_name} executable'))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'❌ Error with {file_name}: {e}'))
        
        self.stdout.write(self.style.SUCCESS('✅ Permission fixing completed'))
