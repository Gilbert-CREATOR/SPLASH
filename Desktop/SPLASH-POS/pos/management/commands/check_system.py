from django.core.management.base import BaseCommand
from django.conf import settings
import os
import sys
import django

class Command(BaseCommand):
    help = 'Check system health and identify potential problems'

    def handle(self, *args, **options):
        self.stdout.write('🔍 SYSTEM HEALTH CHECK')
        self.stdout.write('=' * 50)
        
        problems = []
        warnings = []
        
        # Check database
        db_path = settings.DATABASES['default']['NAME']
        if os.path.exists(db_path):
            db_size = os.path.getsize(db_path) / (1024 * 1024)  # MB
            self.stdout.write(self.style.SUCCESS(f'✅ Database found: {db_size:.2f} MB'))
        else:
            problems.append('Database file not found')
            self.stdout.write(self.style.ERROR('❌ Database file not found'))
        
        # Check directories
        required_dirs = ['media', 'templates', 'pos']
        for dir_name in required_dirs:
            if os.path.exists(dir_name):
                self.stdout.write(self.style.SUCCESS(f'✅ {dir_name}/ directory exists'))
            else:
                problems.append(f'{dir_name}/ directory missing')
                self.stdout.write(self.style.ERROR(f'❌ {dir_name}/ directory missing'))
        
        # Check Django settings
        try:
            self.stdout.write(self.style.SUCCESS(f'✅ Django version: {django.VERSION}'))
        except Exception as e:
            problems.append(f'Django import error: {e}')
            self.stdout.write(self.style.ERROR(f'❌ Django import error: {e}'))
        
        # Check Python version
        python_version = sys.version_info
        if python_version.major >= 3 and python_version.minor >= 8:
            self.stdout.write(self.style.SUCCESS(f'✅ Python version: {python_version.major}.{python_version.minor}.{python_version.micro}'))
        else:
            warnings.append(f'Python version {python_version.major}.{python_version.minor} may be outdated')
            self.stdout.write(self.style.WARNING(f'⚠️  Python version {python_version.major}.{python_version.minor} may be outdated'))
        
        # Check key files
        key_files = ['manage.py', 'requirements.txt']
        for file_name in key_files:
            if os.path.exists(file_name):
                self.stdout.write(self.style.SUCCESS(f'✅ {file_name} exists'))
            else:
                warnings.append(f'{file_name} not found')
                self.stdout.write(self.style.WARNING(f'⚠️  {file_name} not found'))
        
        # Check disk space
        disk_usage = os.statvfs('.')
        free_space = disk_usage.f_bavail * disk_usage.f_frsize / (1024 * 1024 * 1024)  # GB
        if free_space > 1:  # More than 1GB free
            self.stdout.write(self.style.SUCCESS(f'✅ Free disk space: {free_space:.2f} GB'))
        else:
            warnings.append(f'Low disk space: {free_space:.2f} GB')
            self.stdout.write(self.style.WARNING(f'⚠️  Low disk space: {free_space:.2f} GB'))
        
        # Summary
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write('📊 SUMMARY')
        
        if problems:
            self.stdout.write(self.style.ERROR(f'❌ {len(problems)} PROBLEMS FOUND:'))
            for problem in problems:
                self.stdout.write(self.style.ERROR(f'   • {problem}'))
        
        if warnings:
            self.stdout.write(self.style.WARNING(f'⚠️  {len(warnings)} WARNINGS:'))
            for warning in warnings:
                self.stdout.write(self.style.WARNING(f'   • {warning}'))
        
        if not problems and not warnings:
            self.stdout.write(self.style.SUCCESS('✅ System is healthy!'))
        
        # Recommendations
        self.stdout.write('\n💡 RECOMMENDATIONS:')
        if problems:
            self.stdout.write('   • Fix critical problems before continuing')
        if warnings:
            self.stdout.write('   • Address warnings when possible')
        self.stdout.write('   • Run backup regularly: python manage.py backup_system')
        self.stdout.write('   • Monitor system logs for issues')
        self.stdout.write('   • Keep dependencies updated')
