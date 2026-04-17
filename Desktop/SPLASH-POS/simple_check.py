#!/usr/bin/env python3

print("=== VERIFICACIÓN DE USUARIOS ===")

try:
    import os
    import django
    
    # Configurar Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'splash_pos.settings')
    django.setup()
    
    from django.contrib.auth.models import User
    
    # Contar usuarios
    total_users = User.objects.count()
    print(f"Total de usuarios: {total_users}")
    
    # Listar todos los usuarios
    print("\nLista de usuarios:")
    users = User.objects.all().order_by('username')
    for user in users:
        print(f"  - {user.username} (ID: {user.id})")
    
    # Buscar usuario 'empleado'
    print("\n=== BÚSQUEDA DE USUARIO 'empleado' ===")
    try:
        empleado = User.objects.get(username='empleado')
        print("✅ Usuario 'empleado' ENCONTRADO:")
        print(f"   ID: {empleado.id}")
        print(f"   Username: {empleado.username}")
        print(f"   Email: {empleado.email}")
        print(f"   First Name: {empleado.first_name}")
        print(f"   Last Name: {empleado.last_name}")
        print(f"   Is Staff: {empleado.is_staff}")
        print(f"   Is Active: {empleado.is_active}")
        print(f"   Date Joined: {empleado.date_joined}")
        print(f"   Last Login: {empleado.last_login}")
    except User.DoesNotExist:
        print("❌ Usuario 'empleado' NO ENCONTRADO")
        print("Creando usuario 'empleado'...")
        
        # Crear el usuario
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
    
    print("\n=== VERIFICACIÓN FINAL ===")
    final_users = User.objects.all().order_by('username')
    for user in final_users:
        print(f"Username: {user.username}, Staff: {user.is_staff}, Active: {user.is_active}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
