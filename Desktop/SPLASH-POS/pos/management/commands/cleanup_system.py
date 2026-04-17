from django.core.management.base import BaseCommand
import os
import shutil
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Clean up temporary files and optimize system'

    def handle(self, *args, **options):
        self.stdout.write('🧹 SYSTEM CLEANUP')
        self.stdout.write('=' * 40)
        
        # Clean up Python cache files
        cache_patterns = [
            '**/__pycache__',
            '**/*.pyc',
            '**/*.pyo'
        ]
        
        cleaned_files = 0
        cleaned_dirs = 0
        
        # Remove __pycache__ directories
        for root, dirs, files in os.walk('.'):
            if '__pycache__' in dirs:
                cache_dir = os.path.join(root, '__pycache__')
                try:
                    shutil.rmtree(cache_dir)
                    cleaned_dirs += 1
                    self.stdout.write(self.style.SUCCESS(f'✅ Removed {cache_dir}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'❌ Error removing {cache_dir}: {e}'))
        
        # Remove .pyc files
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file.endswith('.pyc') or file.endswith('.pyo'):
                    pyc_file = os.path.join(root, file)
                    try:
                        os.remove(pyc_file)
                        cleaned_files += 1
                        self.stdout.write(self.style.SUCCESS(f'✅ Removed {pyc_file}'))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'❌ Error removing {pyc_file}: {e}'))
        
        # Clean up old backups (keep last 5)
        if os.path.exists('backups'):
            backups = []
            for item in os.listdir('backups'):
                if item.startswith('backup_'):
                    backup_path = os.path.join('backups', item)
                    if os.path.isdir(backup_path):
                        backups.append((backup_path, os.path.getctime(backup_path)))
            
            # Sort by creation time (oldest first)
            backups.sort(key=lambda x: x[1])
            
            # Keep only the 5 most recent
            if len(backups) > 5:
                for backup_path, _ in backups[:-5]:
                    try:
                        shutil.rmtree(backup_path)
                        self.stdout.write(self.style.SUCCESS(f'✅ Removed old backup {backup_path}'))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'❌ Error removing {backup_path}: {e}'))
        
        # Clean up log files (optional)
        log_files = ['debug.log', 'error.log', 'django.log']
        for log_file in log_files:
            if os.path.exists(log_file):
                try:
                    # Check if file is larger than 10MB
                    if os.path.getsize(log_file) > 10 * 1024 * 1024:
                        # Archive old log
                        archive_name = f"{log_file}.old"
                        if os.path.exists(archive_name):
                            os.remove(archive_name)
                        shutil.move(log_file, archive_name)
                        self.stdout.write(self.style.SUCCESS(f'✅ Archived {log_file}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'❌ Error with {log_file}: {e}'))
        
        # Clean up temporary files
        temp_patterns = ['*.tmp', '*.temp', '*.swp', '*.swo']
        for pattern in temp_patterns:
            for root, dirs, files in os.walk('.'):
                for file in files:
                    if file.endswith(tuple([p.replace('*', '') for p in temp_patterns])):
                        temp_file = os.path.join(root, file)
                        try:
                            os.remove(temp_file)
                            cleaned_files += 1
                            self.stdout.write(self.style.SUCCESS(f'✅ Removed temp file {temp_file}'))
                        except Exception as e:
                            self.stdout.write(self.style.ERROR(f'❌ Error removing {temp_file}: {e}'))
        
        # Summary
        self.stdout.write('\n' + '=' * 40)
        self.stdout.write('📊 CLEANUP SUMMARY')
        self.stdout.write(self.style.SUCCESS(f'✅ Files cleaned: {cleaned_files}'))
        self.stdout.write(self.style.SUCCESS(f'✅ Directories cleaned: {cleaned_dirs}'))
        self.stdout.write(self.style.SUCCESS('✅ System cleanup completed'))
        
        # Recommendations
        self.stdout.write('\n💡 RECOMMENDATIONS:')
        self.stdout.write('   • Run cleanup regularly to maintain performance')
        self.stdout.write('   • Monitor disk space usage')
        self.stdout.write('   • Keep backups before major changes')
        self.stdout.write('   • Review log files periodically')
