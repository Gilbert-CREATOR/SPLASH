import subprocess
import sys

try:
    # Test basic Python
    result = subprocess.run([sys.executable, '-c', 'print("Python works")'], 
                         capture_output=True, text=True, timeout=10)
    print("Python test:", result.stdout.strip())
    if result.stderr:
        print("Python stderr:", result.stderr.strip())
    
    # Test Django import
    result = subprocess.run([sys.executable, '-c', 
                         'import django; print("Django version:", django.VERSION)'], 
                         capture_output=True, text=True, timeout=10)
    print("Django test:", result.stdout.strip())
    if result.stderr:
        print("Django stderr:", result.stderr.strip())
    
    # Test Django settings
    result = subprocess.run([sys.executable, '-c', '''
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "splash_pos.settings")
import django
django.setup()
from django.contrib.auth.models import User
count = User.objects.count()
print(f"Users in database: {count}")
for u in User.objects.all().order_by("username"):
    print(f"  - {u.username}")
'''], capture_output=True, text=True, timeout=30)
    print("Django DB test:", result.stdout.strip())
    if result.stderr:
        print("Django DB stderr:", result.stderr.strip())
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
