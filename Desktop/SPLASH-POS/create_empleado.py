#!/usr/bin/env python
import os
import sys

# Add the project directory to the Python path
sys.path.append('/Users/gilbertandeliz/Desktop/SPLASH-POS')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'splash_pos.settings')

import django
django.setup()

from django.contrib.auth.models import User

# Create the empleado user
try:
    # Check if user already exists
    if User.objects.filter(username='empleado').exists():
        print("❌ El usuario 'empleado' ya existe")
        empleado = User.objects.get(username='empleado')
        print(f"   ID: {empleado.id}")
        print(f"   Email: {empleado.email}")
        print(f"   Is Staff: {empleado.is_staff}")
        print(f"   Is Active: {empleado.is_active}")
    else:
        # Create the user
        empleado = User.objects.create_user(
            username='empleado',
            email='empleado@splashpos.com',
            password='emp123',
            first_name='Empleado',
            last_name='Test',
            is_staff=False,
            is_active=True
        )
        print("✅ Usuario 'empleado' creado exitosamente")
        print(f"   Username: {empleado.username}")
        print(f"   Password: emp123")
        print(f"   Email: {empleado.email}")
        print(f"   Is Staff: {empleado.is_staff}")
        print(f"   Is Active: {empleado.is_active}")
        
    # List all users
    print("\n=== TODOS LOS USUARIOS ===")
    users = User.objects.all().order_by('username')
    for user in users:
        print(f"Username: {user.username}, Email: {user.email}, Staff: {user.is_staff}, Active: {user.is_active}")

except Exception as e:
    print(f"❌ Error: {e}")
