"""
CONFIGURACIÓN DE CELERY - B&B CAR WASH
Instrucciones paso a paso para instalar y configurar Celery
"""

# ===================================
# PASO 1: Instalar dependencias
# ===================================

# Ejecuta en terminal:
"""
pip install celery
pip install redis
pip install django-celery-beat
pip install django-celery-results
"""

# Si usas Windows, también instala:
"""
pip install eventlet
"""

# ===================================
# PASO 2: Instalar Redis (Message Broker)
# ===================================

# OPCIÓN 1: Mac con Homebrew
"""
brew install redis
brew services start redis
"""

# OPCIÓN 2: Ubuntu/Debian
"""
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
"""

# OPCIÓN 3: Docker (recomendado para consistencia)
"""
docker run -d -p 6379:6379 --name redis redis:alpine
"""

# OPCIÓN 4: Windows (con WSL o Docker Desktop)
"""
# Usar Docker Desktop
docker run -d -p 6379:6379 --name redis redis:alpine
"""

# ===================================
# PASO 3: Configurar settings.py
# ===================================

# Añade a carwash/settings.py:
"""
# Celery Configuration
import os
from celery import Celery

# Redis Configuration
REDIS_URL = 'redis://localhost:6379/0'

# Celery Settings
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'America/Santo_Domingo'
CELERY_ENABLE_UTC = True

# Celery Beat Settings
CELERY_BEAT_SCHEDULE = {
    'enviar-recordatorios-citas': {
        'task': 'carwashapp.tasks.enviar_recordatorios_citas',
        'schedule': 60.0 * 60.0 * 24.0,  # Cada 24 horas
        'options': {'queue': 'notifications'}
    },
    'verificar-stock-bajo': {
        'task': 'carwashapp.tasks.verificar_stock_bajo',
        'schedule': 60.0 * 60.0 * 2.0,  # Cada 2 horas
        'options': {'queue': 'notifications'}
    },
    'enviar-reporte-diario': {
        'task': 'carwashapp.tasks.enviar_reporte_diario',
        'schedule': 60.0 * 60.0 * 24.0,  # Cada 24 horas
        'options': {'queue': 'reports'}
    },
}

# Django-Celery-Beat
INSTALLED_APPS += [
    'django_celery_beat',
    'django_celery_results',
]

# Database para Celery Beat
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
"""

# ===================================
# PASO 4: Actualizar carwash/__init__.py
# ===================================

# Asegúrate de que carwash/__init__.py contenga:
"""
from .celery import app as celery_app

__all__ = ('celery_app',)
"""

# ===================================
# PASO 5: Migrar base de datos para Celery Beat
# ===================================

"""
python manage.py migrate django_celery_beat
python manage.py migrate django_celery_results
"""

# ===================================
# PASO 6: Scripts de inicio
# ===================================

# Crea start_celery.sh (Mac/Linux):
"""
#!/bin/bash

echo "Iniciando Redis..."
redis-server --daemonize yes

echo "Iniciando Celery Worker..."
celery -A carwash worker -l info --detach

echo "Iniciando Celery Beat..."
celery -A carwash beat -l info --detach

echo "✅ Servicios Celery iniciados"
"""

# Crea start_celery.bat (Windows):
"""
@echo off
echo Iniciando Redis...
redis-server --daemonize yes

echo Iniciando Celery Worker...
start /B celery -A carwash worker -l info

echo Iniciando Celery Beat...
start /B celery -A carwash beat -l info

echo ✅ Servicios Celery iniciados
pause
"""

# Haz ejecutable el script (Mac/Linux):
"""
chmod +x start_celery.sh
"""

# ===================================
# PASO 7: Comandos de verificación
# ===================================

# Verificar conexión Redis:
"""
redis-cli ping
# Debe responder: PONG
"""

# Verificar workers activos:
"""
celery -A carwash inspect active
"""

# Verificar tareas programadas:
"""
celery -A carwash beat schedule
"""

# Verificar estadísticas:
"""
celery -A carwash stats
"""

# ===================================
# PASO 8: Monitoreo (Opcional)
# ===================================

# Instalar Flower para monitoreo web:
"""
pip install flower
"""

# Iniciar Flower:
"""
celery -A carwash flower
# Visita: http://localhost:5555
"""

# ===================================
# TROUBLESHOOTING
# ===================================

PROBLEMAS_COMUNES = {
    "Redis no conecta": """
        1. Verifica que Redis esté corriendo: redis-cli ping
        2. Verifica puerto: netstat -an | grep 6379
        3. Revisa firewall: sudo ufw allow 6379
    """,
    
    "Celery worker no inicia": """
        1. Verifica importación: python -c "from carwashapp.tasks import test"
        2. Revisa configuración en settings.py
        3. Inicia con modo verbose: celery -A carwash worker -l debug
    """,
    
    "Tareas no se ejecutan": """
        1. Verifica queues: celery -A carwash inspect registered
        2. Revisa logs de worker
        3. Prueba tarea manual: celery -A carwash call carwashapp.tasks.enviar_recordatorios_citas
    """,
    
    "Celery Beat no funciona": """
        1. Verifica tabla django_celery_beat_periodictask
        2. Revisa timezone settings
        3. Reinicia beat: celery -A carwash beat -l debug
    """
}

# ===================================
# CONFIGURACIÓN PARA PRODUCCIÓN
# ===================================

PRODUCTION_CONFIG = """
# Usar Redis con persistencia
redis-server --appendonly yes --save 900 1

# Configurar workers con concurrencia
celery -A carwash worker -c 4 --loglevel=info

# Configurar beat con lock
celery -A carwash beat --max-interval=60.0

# Usar supervisor para gestión de procesos
# Instalar: pip install supervisor
# Configurar en /etc/supervisor/conf.d/celery.conf
"""
