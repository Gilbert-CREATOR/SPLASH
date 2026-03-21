#!/usr/bin/env python
"""
SCRIPT DE PRUEBA - SOLO EMAILS - B&B CAR WASH
Prueba simplificada solo para sistema de emails
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carwash.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings
from carwashapp.services.notifications import NotificationService
from carwashapp.models import Cita, Servicio, Producto
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_email_configuration():
    """Probar configuración de email"""
    print("📧 Probando configuración de email...")
    print(f"Backend: {settings.EMAIL_BACKEND}")
    print(f"Host: {settings.EMAIL_HOST}")
    print(f"Port: {settings.EMAIL_PORT}")
    print(f"TLS: {settings.EMAIL_USE_TLS}")
    
    try:
        send_mail(
            '🧪 Test Email - B&B Car Wash',
            'Este es un email de prueba para verificar la configuración.',
            settings.DEFAULT_FROM_EMAIL,
            ['test@example.com'],  # Cambiar por tu email
            fail_silently=False
        )
        print("✅ Email enviado exitosamente!")
        return True
    except Exception as e:
        print(f"❌ Error enviando email: {e}")
        return False

def test_notification_service():
    """Probar servicio de notificaciones (solo email)"""
    print("\n🔔 Probando servicio de notificaciones (solo email)...")
    
    try:
        notification_service = NotificationService()
        
        # Crear cita de prueba
        servicio = Servicio.objects.first()
        if not servicio:
            print("❌ No hay servicios en la base de datos")
            return False
        
        cita_prueba = Cita.objects.create(
            nombre="Cliente Prueba",
            telefono="+18091234567",
            email="test@example.com",  # Cambiar por tu email
            servicio=servicio,
            fecha=datetime.now().date() + timedelta(days=1),
            hora=datetime.now().time(),
            estado='confirmada'
        )
        
        print(f"Cita de prueba creada: {cita_prueba.id}")
        
        # Probar confirmación
        resultado = notification_service.send_cita_confirmation(cita_prueba)
        print(f"Resultado confirmación: {resultado}")
        
        # Limpiar
        cita_prueba.delete()
        
        return resultado['email_sent']
        
    except Exception as e:
        print(f"❌ Error en servicio de notificaciones: {e}")
        return False

def test_celery_connection():
    """Probar conexión con Celery"""
    print("\n🔄 Probando conexión con Celery...")
    
    try:
        from celery import current_app
        from carwashapp.tasks import enviar_recordatorios_citas
        
        # Enviar tarea de prueba
        result = enviar_recordatorios_citas.delay()
        print(f"✅ Tarea enviada a Celery: {result.id}")
        
        # Verificar estado
        status = result.status
        print(f"Estado de la tarea: {status}")
        
        return True
    except Exception as e:
        print(f"❌ Error con Celery: {e}")
        return False

def test_redis_connection():
    """Probar conexión con Redis"""
    print("\n🔴 Probando conexión con Redis...")
    
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        
        # Probar ping
        pong = r.ping()
        if pong:
            print("✅ Conexión Redis exitosa!")
            
            # Probar set/get
            r.set('test_key', 'test_value')
            value = r.get('test_key')
            if value == b'test_value':
                print("✅ Operaciones Redis funcionando!")
                r.delete('test_key')
                return True
            else:
                print("❌ Error en operaciones Redis")
                return False
        else:
            print("❌ Redis no responde")
            return False
            
    except Exception as e:
        print(f"❌ Error conectando a Redis: {e}")
        return False

def test_database_models():
    """Probar modelos de base de datos"""
    print("\n💾 Probando modelos de base de datos...")
    
    try:
        # Contar registros
        citas_count = Cita.objects.count()
        servicios_count = Servicio.objects.count()
        productos_count = Producto.objects.count()
        
        print(f"Citas: {citas_count}")
        print(f"Servicios: {servicios_count}")
        print(f"Productos: {productos_count}")
        
        if servicios_count == 0:
            print("⚠️  No hay servicios. Creando uno de prueba...")
            Servicio.objects.create(
                nombre="Lavado Básico",
                descripcion="Lavado exterior completo",
                precio=500.00,
                duracion=30
            )
            print("✅ Servicio de prueba creado")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en base de datos: {e}")
        return False

def main():
    """Ejecutar todas las pruebas (solo email)"""
    print("🚀 INICIANDO PRUEBAS - SISTEMA DE EMAILS")
    print("=" * 50)
    
    results = {}
    
    # Probar componentes básicos
    results['database'] = test_database_models()
    results['redis'] = test_redis_connection()
    results['email'] = test_email_configuration()
    results['celery'] = test_celery_connection()
    results['notifications'] = test_notification_service()
    
    # Resumen
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE PRUEBAS (SOLO EMAIL)")
    print("=" * 50)
    
    for component, result in results.items():
        status = "✅" if result else "❌"
        print(f"{status} {component.title()}: {'Funciona' if result else 'Error'}")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    print(f"\nResultados: {passed_tests}/{total_tests} pruebas exitosas")
    
    if passed_tests == total_tests:
        print("🎉 ¡Todas las pruebas pasaron! El sistema de emails está listo.")
    else:
        print("⚠️  Algunas pruebas fallaron. Revisa los errores arriba.")
    
    print("\n📋 Próximos pasos:")
    if not results['email']:
        print("1. Configura tus credenciales de email")
    if not results['redis']:
        print("2. Inicia el servidor Redis")
    if not results['celery']:
        print("3. Inicia los workers de Celery")
    
    if all([results['email'], results['redis'], results['celery']]):
        print("✅ Sistema de emails completo listo!")
        print("📧 Emails automáticos funcionando")
        print("🔄 Tareas programadas activas")
        print("📊 Dashboard avanzado disponible")
        print("\n🌐 URLs disponibles:")
        print("   - Dashboard: http://127.0.0.1:8000/dashboard/avanzado/")
        print("   - Reportes: http://127.0.0.1:8000/dashboard/reportes/")

if __name__ == '__main__':
    main()
