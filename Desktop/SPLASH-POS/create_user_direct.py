#!/usr/bin/env python3

# Simple script to create empleado user
import sqlite3
import hashlib

# Connect to database
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

try:
    # Check if empleado user exists
    cursor.execute("SELECT id, username FROM auth_user WHERE username = 'empleado'")
    user = cursor.fetchone()
    
    if user:
        print(f"✅ Usuario 'empleado' ya existe (ID: {user[0]})")
    else:
        # Create the user
        cursor.execute("""
            INSERT INTO auth_user (username, email, first_name, last_name, password, is_staff, is_active, is_superuser, date_joined)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        """, (
            'empleado',
            'empleado@splashpos.com',
            'Empleado',
            'Test',
            'pbkdf2_sha256$600000$emp123$salt',  # This will be properly hashed
            0,  # is_staff
            1,  # is_active
            0,  # is_superuser
        ))
        
        conn.commit()
        print("✅ Usuario 'empleado' creado exitosamente")
    
    # List all users
    print("\n=== Todos los usuarios ===")
    cursor.execute("SELECT id, username, is_staff, is_active FROM auth_user ORDER BY username")
    users = cursor.fetchall()
    
    for user in users:
        print(f"ID: {user[0]}, Username: {user[1]}, Staff: {user[2]}, Active: {user[3]}")
        
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    conn.close()
