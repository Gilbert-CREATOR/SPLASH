#!/usr/bin/env python
import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'splash_pos.settings')
django.setup()

from django.contrib.auth.models import User

# Check all users
print("=== USUARIOS EN EL SISTEMA ===")
users = User.objects.all().order_by('username')
for user in users:
    print(f"ID: {user.id}")
    print(f"Username: {user.username}")
    print(f"Email: {user.email}")
    print(f"First Name: {user.first_name}")
    print(f"Last Name: {user.last_name}")
    print(f"Is Staff: {user.is_staff}")
    print(f"Is Active: {user.is_active}")
    print(f"Last Login: {user.last_login}")
    print(f"Date Joined: {user.date_joined}")
    print("-" * 40)

# Check specifically for 'empleado'
print("\n=== BUSCANDO USUARIO 'empleado' ===")
try:
    empleado_user = User.objects.get(username='empleado')
    print(f"✅ Usuario 'empleado' encontrado:")
    print(f"   ID: {empleado_user.id}")
    print(f"   Email: {empleado_user.email}")
    print(f"   Is Staff: {empleado_user.is_staff}")
    print(f"   Is Active: {empleado_user.is_active}")
except User.DoesNotExist:
    print("❌ Usuario 'empleado' NO encontrado")

# Check for similar usernames
print("\n=== USUARIOS SIMILARES ===")
similar_users = User.objects.filter(username__contains='emple').order_by('username')
for user in similar_users:
    print(f"- {user.username} (ID: {user.id})")
